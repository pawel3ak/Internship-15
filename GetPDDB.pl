#!/usr/bin/perl

use strict;
use LWP;
use IO::File;
use XML::Twig;
use Getopt::Long;

my %opts;

my $err = 'Invalid syntax';
local $SIG{__WARN__} = sub { $err = join '', @_ };

unless (GetOptions(\%opts, 'file=s')) {
    print "* ERROR: $err\n";
    exit 0;
}

my $in_file   = '';
my $out_file  = '';
my $out_dir   = '../pddb/';
my $pddb_map_file = "PDDB_Releases.pl";

my $out_label = '';
my $id_str;

our %PDDB_MAP;

my %classes;

my %change_string_map = (
    'onLine'       => 'On-line',
    'unmodifiable' => 'Not modifiable',
);

my %required_string_map = (
    'mandatory' => 'Mandatory',
    'optional'  => 'Optional',
);


if ($opts{'file'}) {
    $in_file = $opts{'file'};

    unless (-e $in_file) {
        print "* Error: File: $in_file does not exist !!!\n";
        exit 0;
    }

    unless (-s $in_file) {
        print "* Error: File: $in_file is empty !!!\n";
        exit 0;
    }

    unless (-r $in_file) {
        print "* Error: File: $in_file cannot be read !!!\n";
        exit 0;
    }
}
else {
    $id_str = shift @ARGV;

    unless (defined $id_str && $id_str =~ /^\d+(,\d+)*$/) {
        print "* Error: Wrong format of PDDB release id. Comma separated decimal numbers expected !!!\n";
        exit 0;
    }

    $in_file = './pddb_dump.xml';
}

# something else was provided - garbage
if (@ARGV) {
    print "* Error: Unexpected arguments: " . join(", ", @ARGV) . "\n";
    exit 0;
}

# step 1
unless ($opts{'file'}) {
    my $LIMIT = 3;  # number of attempts
    my $tout = 600; # PDDB export timeout
    my $host = 'pddb.inside.nokiasiemensnetworks.com';
    my $count;
    my $export_status;
    my $url;
    my $doc_path;
    my @releases = split(/,/, $id_str);

    my $browser = LWP::UserAgent->new;
    $browser->timeout($tout);

    foreach my $rel_id (@releases) {
        next if pddb_release_exists($rel_id);

        $export_status = 0;
        $count = 0;

        $doc_path = '/pddb/reports/Report.do?relid=' . $rel_id . '&basereleaseincluded=yes&hiddenincluded=no&deletedincluded=no';
        $url = 'http://' . $host . $doc_path;

        print_action("Working for release id: $rel_id");

        print_action("Step 1: Exporting PDDB metadata ...");
        print "* URL: $url\n* Download inactivity timeout: $tout seconds\n";

        while (++$count <= $LIMIT) {
            print "* Attempt #$count\n";
            my $DlStartT = time();
            my $response = $browser->get($url, ':content_file' => $in_file);
            my $DlDur = time() - $DlStartT;

            print "* #$count Download duration: $DlDur seconds\n";

            if ($response->is_success()) {
                print "* #$count Data stored at: $in_file\n";
                $export_status = 1;
                last;
            }
            else {
                print "* #$count ERROR: " . $response->status_line() . "\n";
                next;
            }
        }

        unless ($export_status) {
            print "* ERROR: Retry limit reached\n";
            next;
        }

        parse_metadata();
        update_pddb_mapping($rel_id);
    }
}
else {
    parse_metatdata();
}

print_action("Finish");

################################################################################

sub parse_metadata {

    print_action("Step 2: Parsing PDDB metadata ...");

    %classes = ();

    my $twig = new XML::Twig(
      TwigHandlers => {
          'header'        => sub {   header(@_) },
          'managedObject' => sub { visit_mo(@_) }
      },
      keep_encoding => 1
    );

    my $ParseStartT = time();

    unless ($twig->safe_parsefile($in_file)) {
        print "* ERROR: XML File $in_file: $@";
        return;
    };

    my $ParseDur = time() - $ParseStartT;
    print "* Parse duration: $ParseDur seconds\n";
    $twig->purge();

    if (keys %classes) {
        my $fh;
        exit unless defined ($fh = new IO::File "> $out_file");
        my $result_hash = \%classes; #remove !!!
        my $dump;
        my $topo_dump;
        my $head = '%PDDB = (' . "\n";
        my $topo_head = '%PDDB_TOPO = (' . "\n";
        my $tail = ");\n";

        $dump      .= $head;
        $topo_dump .= $topo_head;

        foreach my $class (sort keys %{$result_hash}) {
            $dump .=      "    " . uc($class) . " => {\n";
            $topo_dump .= "    " . uc($class) . " => {\n";

            my $index = '';

            my $params = $result_hash->{$class}->{'parameters'};
            foreach my $parameter (sort keys %{$params}) {
                my $human  = $params->{$parameter}->{'human'};
                my $def    = $params->{$parameter}->{'default'};
                my $type   = $params->{$parameter}->{'type'};
                my $range  = $params->{$parameter}->{'range'};
                my $spec   = $params->{$parameter}->{'special'};
                my $req    = $params->{$parameter}->{'required'};
                my $change = $params->{$parameter}->{'change'};
                my $struct = $params->{$parameter}->{'structure'};
                my $multi  = $params->{$parameter}->{'count'};
                my $wtrans = $params->{$parameter}->{'wtrans'};
                my $rtrans = $params->{$parameter}->{'rtrans'};

                $index = $parameter if $params->{$parameter}->{'index'};

                $dump .= "        '$parameter' => {\n";
                $dump .= "            'human'    => '$human',\n";
                $dump .= "            'default'  => '$def',\n";
                $dump .= "            'type'     => '$type',\n";
                $dump .= "            'range'    => '$range',\n";
                $dump .= "            'special'  => '$spec',\n" if defined $spec;
                $dump .= "            'required' => '$req',\n";
                $dump .= "            'change'   => '$change',\n";
                $dump .= "            'count'    => '$multi',\n";
                $dump .= "            'wtrans'   =>  $wtrans,\n";
                $dump .= "            'rtrans'   =>  $rtrans,\n";
                
                if (ref $struct eq 'HASH') {
                    my $struct_dump = '';
                    $struct_dump .= "            'struct'   => {\n";
                    foreach my $key (sort keys %{$struct}) {
                        my $s_human = $struct->{$key}->{'human'};
                        my $s_def    = $struct->{$key}->{'default'};
                        my $s_type   = $struct->{$key}->{'type'};
                        my $s_range  = $struct->{$key}->{'range'};
                        my $s_spec   = $struct->{$key}->{'special'};
                        my $s_req    = $struct->{$key}->{'required'};
                        my $s_change = $struct->{$key}->{'change'};
                        my $s_struct = $struct->{$key}->{'struct'};
                        my $s_multi  = $struct->{$key}->{'count'};
                        my $s_wtrans = $struct->{$key}->{'wtrans'};
                        my $s_rtrans = $struct->{$key}->{'rtrans'};

                        $struct_dump .= "                '$key' => {\n";
                        $struct_dump .= "                    'human'    => '$s_human',\n";
                        $struct_dump .= "                    'default'  => '$s_def',\n";
                        $struct_dump .= "                    'type'     => '$s_type',\n";
                        $struct_dump .= "                    'range'    => '$s_range',\n";
                        $struct_dump .= "                    'special'  => '$s_spec',\n" if defined $s_spec;
                        $struct_dump .= "                    'required' => '$s_req',\n";
                        $struct_dump .= "                    'change'   => '$s_change',\n";
                        $struct_dump .= "                    'count'    => '$s_multi',\n";
                        $struct_dump .= "                    'wtrans'   =>  $s_wtrans,\n";
                        $struct_dump .= "                    'rtrans'   =>  $s_rtrans,\n";
                        $struct_dump .= "                },\n";
                    }
                    $struct_dump .= "            },\n";
                    $dump .= $struct_dump;
                }
                else {
                    $dump .= "            'struct'   => '$struct',\n";
                }
                $dump .= "        },\n";
            }
            $dump .= "    },\n";

            my $number = $result_hash->{$class}->{'count'};
            my $parent = $result_hash->{$class}->{'parent'};
            $topo_dump .= "        'parent' => '$parent',\n";
            $topo_dump .= "        'number' => '$number',\n";
            $topo_dump .= "        'index'  => '$index',\n";
            $topo_dump .= "    },\n";
        }

        $dump      .= $tail;
        $topo_dump .= $tail;

        print $fh $dump;
        print $fh $topo_dump;

        print "* Generated file for EMSSim: $out_file\n";

        print_action("Step 3: Propagating file...");

        transfer_file('emssim-2');
        transfer_file('emssim-vir');

        print_action("Step 4: Updating git repo...");

        git_update();
    }
}

################################################################################

sub transfer_file {
    my $hostname = shift;

    my %hosts = (
      'emssim-2'   => {'ip'   => '10.83.202.52',
                       'path' => '/emss/pddb/'
                      },

      'emssim-vir' => {'ip'   => '10.83.205.71',
                       'path' => '/pddb/'
                      },
    );

    my $host_data = $hosts{$hostname};

    unless ($host_data) {
        print "* ERROR: Unrecognized hostname: $hostname\n";
        return;
    }

    my $host = $host_data->{'ip'};
    my $path = $host_data->{'path'};

    my $credentials = 'emssim:emssim';

    my $url = 'ftp://' . $host . $path;

    my $curl = `curl -k -s -u $credentials --noproxy $host -T $out_file $url 2>&1`;

    if ($curl =~ /curl\: \(\d+\)/) {
        print "* ERROR: Cannot transfer generated file: $curl\n";
        return;
    }

    print "* File transfered to $host machine\n";
}

################################################################################

sub git_update {
    print "* git add $out_file\n";
    my $git_status = `git add $out_file 2>&1`;

    if (${^CHILD_ERROR_NATIVE}) {
        print "Error: git add problem:\n$git_status\n";
        return;
    }

    my $git_msg = '"New PDDB export: ' . $out_label . '.txt"';
    print "* git commit -m $git_msg\n";
    $git_status = `git commit -m $git_msg 2>&1`;

    if (${^CHILD_ERROR_NATIVE}) {
        print "Error: git commit problem:\n$git_status\n";
        return;
    }

    print "*** Remember to perform git pull/git push operations\n";
}

################################################################################

sub pddb_release_exists {
    my $rel_id = shift;

    do $pddb_map_file;

    if (grep { $_ == $rel_id } (keys %PDDB_MAP)) {

        my $label = $PDDB_MAP{$rel_id};

        opendir my $dir, $out_dir or die "Cannot open directory: $!";
        my @files = readdir $dir;
        closedir $dir;

        if (grep { $_ =~ /^$label/ } (@files)) {
            print "* Release Id: $rel_id, Label: $label - Export file already exists\n";
            return 1;
        }
    }
    return 0;
}

################################################################################

sub update_pddb_mapping {
    my $rel_id = shift;
    my $pddb_fd;

    unless (grep { $_ == $rel_id } (keys %PDDB_MAP)) {
        return unless defined ($pddb_fd = new IO::File "> $pddb_map_file");

        $PDDB_MAP{$rel_id} = $out_label;

        my $h = '%PDDB_MAP = (' . "\n";
        my $t = ');';

        print $pddb_fd $h;
        my $line;
        foreach (sort { $b <=> $a } (keys %PDDB_MAP)) {
            $line = '    ' . $_ . " => '" . $PDDB_MAP{$_} . "',\n";
            print $pddb_fd $line;
        }
        print $pddb_fd $t;

        close $pddb_fd;
    }
    return;
}

################################################################################

sub visit_mo {
    my (undef, $crt) = @_;
    my $class  = $crt->att('class');
    my $hidden = $crt->att('hidden');
    my $create = $crt->att('create');
    my $update = $crt->att('update');
    my $delete = $crt->att('delete');
    my @childs = $crt->children('childManagedObject');

    foreach my $child (@childs) {
        my ($cc, $cn) = ($child->att('class'), $child->att('maxOccurs'));
        $cn = 'unlimited' unless $cn;
        $classes{$cc}{'parent'} = $class;
        $classes{$cc}{'count'}  = $cn;
    }

    # manual fix !!!
    if ($class eq 'MRBTS') {
        $classes{$class}{'parent'} = '';
        $classes{$class}{'count'} = 1;
    }

    my @pchilds = $crt->children('p');
    foreach my $pchild (@pchilds) {
        my $pdata = get_parameter_data($pchild);
        next unless $pdata;
        foreach (keys %{$pdata}) {
            $classes{$class}{'parameters'}{$_} = $pdata->{$_};
        }
    }


    $classes{$class}{'hidden'} = $hidden;
    $classes{$class}{'create'} = $create;
    $classes{$class}{'update'} = $update;
    $classes{$class}{'delete'} = $delete;
    $crt->purge();
    return 1;
}

################################################################################

sub get_parameter_data {
    my $pchild = shift;
    my %result;
    my $name   = $pchild->att('name');
    my $fname  = $pchild->att('fullName');
    my $count  = $pchild->att('maxOccurs');

    my $pri    = $pchild->first_child('creation');
    my $man;

    if ($pri) {
        $man = $pri->att('priority');
    }
    else {
        $man = 'Mandatory';
        print "Warning: suspicious parameter: $name (no creation rule defined), assuming: 'Mandatory'\n";
    }

    my $mod    = $pchild->first_child('modification');
    my $change;

    if ($mod) {
        $change = $mod->att('type');
    }
    else {
        $change = 'unmodifiable';
        print "Warning: suspicious parameter: $name (no modification rule defined), assuming: 'unmodifiable'\n";
    }

    my $type;
    my $default = '';
    my $range   = '';
    my $special = undef;
    my $structure = '';
    my $wtrans = 'sub { return shift }';
    my $rtrans = $wtrans;
    my $index  = 0;

    if ($pchild->has_child('simpleType')) {
        my $st = $pchild->first_child('simpleType');
        $type = $st->att('base');
        if ($st->has_child('default')) {
            my $dflt_child = $st->first_child('default');
            $default = $dflt_child->att('value');
        }
        if ($type eq 'integer') {
            if ($st->has_child('enumeration')) {
                my @enum_childs = $st->children('enumeration');
                my %range_map;
                my @range_list;
                foreach my $ec (@enum_childs) {
                    my ($ev, $et) = ($ec->att('value'), $ec->att('text'));
                    $range_map{$ev} = $et;
                    push @range_list, "$et ($ev)"
                }

                $range = join(",", @range_list);

                if ($default ne '') {
                    $default = $range_map{$default};
                }
                $type = 'Enumeration';
            }
            elsif ($st->has_child('bit')) {
                my @range_list;
                my @bit_childs = $st->children('bit');
                foreach my $bc (@bit_childs) {
                    my ($bv, $bt) = ($bc->att('number'), $bc->att('text'));
                    push @range_list, "Bit $bv: $bt";
                }
                $range = join(",", @range_list);
                $type = 'Bitmask';
            }
        }
        elsif ($type eq 'decimal') {
            if ($st->has_child('editing')) {
                my $edit_child = $st->first_child('editing');
                my $int_val = $edit_child->att('internalValue');
                my $units = $edit_child->att('units');
                my $div   = $edit_child->att('divisor');
                my $mul   = $edit_child->att('multiplicand');
                my $shift = $edit_child->att('shift');
                if ($shift or $mul or $div) {
                    my $head = 'sub { my $in = shift; return ';
                    my $tail = ($div) ? ' * ' . $div . '; }' : '; }';
                    $tail = ' / ' . $mul . $tail if $mul;
                    $shift =~ s/-//;
                    my $inner = '$in';
                    if ($shift) {
                        $inner .= ' + ' . $shift;
                        $inner = '('.$inner.')' if ($div or $mul);
                    }
                    $wtrans = $head.$inner.$tail;

                    $rtrans = $head . '$in';
                    $rtrans .= ' / ' . $div   if $div;
                    $rtrans .= ' * ' . $mul   if $mul;
                    $rtrans .= ' - ' . $shift if $shift; 
                    $rtrans .= '; }';
                }
                if ($edit_child->has_child('range')) {
                    my $range_child = $edit_child->first_child('range');
                    my $min  = $range_child->att('minIncl');
                    my $max  = $range_child->att('maxIncl');
                    my $step = $range_child->att('step') || 1;
                    $range = "$min...$max";
                    $range .= ($units) ? " $units" : '';
                    if ($step) {
                        my $step_str .= ", step $step";
                        $step_str .= ($units) ? " $units" : '';
                        $range .= $step_str;
                    }
                }
                if ($edit_child->has_child('default')) {
                    my $dc = $edit_child->first_child('default');
                    $default = $dc->att('value');
                }
            }
            if ($st->has_child('special')) {
                my $sp = $st->first_child('special');
                $special = $sp->att('value');
            }
            $type = 'Number';
        }
        elsif ($type eq 'string') {
            my $min = 0;
            my $max = 0;
            if ($st->has_child('length')) {
                my $len_child = $st->first_child('length');
                $min = $len_child->att('value');
                $max = $min;
            }
            else {
                if ($st->has_child('minLength')) {
                    my $min_child = $st->first_child('minLength');
                    $min = $min_child->att('value');
                }
                if ($st->has_child('maxLength')) {
                    my $max_child = $st->first_child('maxLength');
                    $max = $max_child->att('value');
                }
            }
            $range = "$min...$max characters";
            $type = 'String';
        }
        elsif ($type eq 'boolean') {
            $range = 'false, true';
            $type = 'Boolean';
        }
    }
    else {
        my $st = $pchild->first_child('complexType');
        $type = 'Structure';
        my %struct_hash;
        my @schilds = $st->children('p');
        foreach my $schild (@schilds) {
            my $sdata = get_parameter_data($schild);
            foreach (keys %{$sdata}) {
                $struct_hash{$_} = $sdata->{$_};
            }
        }
        $structure = \%struct_hash;
    }

    my @pdchilds = $pchild->children('productData');
    foreach my $pdchild (@pdchilds) {
        if ($pdchild->att('name') eq 'RAC') {
            my @properties = $pdchild->children('property');
            foreach my $pd_property (@properties) {
                if ($pd_property->att('value') eq '$instance') {
                    $index = 1;
                }
            }
        }
    }

    $result{$name}{'human'}     = $fname;
    $result{$name}{'count'}     = $count;
    $result{$name}{'required'}  = $required_string_map{$man}  || $man;
    $result{$name}{'change'}    = $change_string_map{$change} || $change;
    $result{$name}{'type'}      = $type;
    $result{$name}{'default'}   = $default;
    $result{$name}{'range'}     = $range;
    $result{$name}{'special'}   = $special;
    $result{$name}{'wtrans'}    = $wtrans;
    $result{$name}{'rtrans'}    = $rtrans;
    $result{$name}{'structure'} = $structure;
    $result{$name}{'index'}     = $index;

    return \%result;
}

################################################################################

sub header {
    my (undef, $crt) = @_;
    my $rel    = $crt->att('release');
    my $ver    = $crt->att('version');
    my $prod   = $crt->att('product');
    my $domain = $crt->att('domain');

    unless ($domain eq "LTE" and $prod eq "LTE BTS") {
        print "* ERROR: Wrong domain or product detected: $domain, $prod";
        return;
    }
    $out_label = $rel . '_' . $ver;
    $out_file  = $out_dir . $out_label . '.txt';
}

################################################################################

sub print_action {
    my $info = shift;
    my $line = "-" x 60;
    print $line . "\n";
    print $info . "\n";
    print $line . "\n";
}

################################################################################
