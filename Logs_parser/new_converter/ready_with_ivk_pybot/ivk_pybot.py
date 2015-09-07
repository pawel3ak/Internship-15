################################################################################
# NSN Copyright (C) 2015. All rights reserved.                                 #
# LTE eNB Box Test, GSG Poland                         #
################################################################################

import sys
import time
import os
from argparse import ArgumentParser

from robot import run, rebot
from ruff import TMgr
import yaml


def main():
    startTime = time.time()
    print time.strftime(' - %H:%M:%S %d/%m/%Y -')

    parser = ArgumentParser(description="RUFF test luncher")
    parser.add_argument('-S', '--tests', dest="tests_source", required=True)
    parser.add_argument('-c', '--config', dest="config_path", required=True)
    parser.add_argument('-d', '--outputdir', dest="outputdir", default=time.strftime('%Y-%m-%d_%H-%M-%S'))
    parser.add_argument('-o', '--output', dest="output", default="output.xml")
    parser.add_argument('-l', '--log', dest="log", default="log.html")
    parser.add_argument('-r', '--report', dest="report", default="report.html")
    parser.add_argument('-L', '--loglevel', dest="loglevel", default="INFO")
    parser.add_argument('--actiononfailure', dest="action_on_failure", default="continue",
                        choices=['continue', 'rerun', 'stop'])
    parser.add_argument('--record', dest="record", action='store_true', default=False,
                        help="record TAF connections for replay via '--play connection'")
    parser.add_argument('--play', dest="play", default="not",
                        help="'rpc' - replay based on rpc logs, 'connection' - replay based on connection logs"
                             ", exacttime - will keep recorded timing when replaying, maxspeed - replay as fast as possible",
                        choices=['rpc', 'connection:maxspeed', 'connection:exacttime'])
    parser.add_argument('-f', '--feature', dest="feature", default="")

    options = parser.parse_args()
    tests, tags, variables, excludes = parse_config_file(options.config_path)
    tests = {key : tests[key] for key in tests.keys() if options.feature in key}
    suites = build_suites(tests)
    run_tests(options, suites, tags, variables, excludes)
    os.system("python taf_logs_converter.py >> /dev/null")

    endTime = time.time()
    print time.strftime(' - %H:%M:%S %d/%m/%Y -')
    print elapsed_time(endTime, startTime)

def elapsed_time(endTime, startTime):
    t = endTime - startTime
    printout = 'Elapsed time: '
    printout += str(int(t/3600)).zfill(2)+':'
    t = t%3600
    printout += str(int(t/60)).zfill(2)+':'
    t = t%60
    printout += str(round(t, 1)).zfill(4)
    return printout

def parse_tests(dict_of_tests):
    tests = {}
    for item in dict_of_tests:
        if not isinstance(item, dict):
            tests[str(item)] = 1
        else:
            for key, value in item.items():
                tests[str(key)] = value
    return tests


def parse_tags(dict_of_tags):
    tags = []
    for tag in dict_of_tags:
        tags.append(tag)
    return tags


def parse_variables(dict_of_variables):
    variables = []
    for item in dict_of_variables:
        for key, value in item.items():
            variables.append(str(key) + ":" + str(value))
    return variables


def parse_excludes(dict_of_excludes):
    excludes = []
    for exclude in dict_of_excludes:
        excludes.append(exclude)
    return excludes


def parse_config_file(path_to_config):
    with open(path_to_config, 'r') as config_file:
        config_dict = yaml.load(config_file)
    config_file.close()
    tests = {}
    tags = []
    excludes = []
    variables = []
    if config_dict["variables"]:
        variables = parse_variables(config_dict["variables"])

    if config_dict["excluded_tags"]:
        excludes = parse_excludes(config_dict["excluded_tags"])

    if config_dict["tags"]:
        tags = parse_tags(config_dict["tags"])

    if config_dict["test_instances"]:
        tests = parse_tests(config_dict["test_instances"])

    return tests, tags, variables, excludes


def build_single_suite(uncovered_tests):
    single_suite = []
    for test, times in uncovered_tests.items():
        if times > 0:
            single_suite.append(test)
            uncovered_tests[test] -= 1
        else:
            del uncovered_tests[test]
    return single_suite


def build_suites(tests):
    uncovered_tests = dict(tests)
    suites = []
    while uncovered_tests:
        single_suite = build_single_suite(uncovered_tests)
        if single_suite:
            suites.append(single_suite)
    return suites


def stop_on_suite_failure_(status, outputs, options, suite):
    merge_outputs(outputs, options)
    sys.exit(repr(suite) + " Test suite execution ended with error")


def stop_on_suite_failure(status, out, options, suite):
    # todo implement rerun metod
    print "Not implemented yet"


def merge_outputs(outputs, options):
    rebot(*outputs, output=options.output, outputdir=options.outputdir)

def handle_player_preparation(options):
    os.environ['RUFF_PLAY'] = options.play
    if options.record:
        os.environ['RUFF_RECORD'] = '1'

def handle_player_cleanup(options):
    if 'connection' in options.play:
        # kill TAF server to be sure no mocked devices remain for next non-play-run
        TMgr.stop_taf_server()

def run_tests(options, suites, tags, variables, excludes):
    outputs = []
    i = 0

    handle_player_preparation(options)

    for suite in suites:
        i += 1
        output_name = 'suite_%s.xml' % str(i)
        status = run(options.tests_source, test=suite, include=tags, exclude=excludes, variable=variables,
                     outputdir=options.outputdir,
                     output=output_name, log=options.log, report=options.report, loglevel=options.loglevel)
        print output_name
        if options.outputdir.startswith('/'):
            outputs.append(options.outputdir + '/' + output_name)
        else:
            outputs.append('./' + options.outputdir + '/' + output_name)
        if status > 0:
            if options.action_on_failure == 'continue':
                pass
            elif options.action_on_failure == 'rerun':
                stop_on_suite_failure(status, outputs, options, suite)
            elif options.action_on_failure == 'stop':
                stop_on_suite_failure_(status, outputs, options, suite)

    if outputs:
        merge_outputs(outputs, options)

    handle_player_cleanup(options)

if __name__ == "__main__":
    main()
