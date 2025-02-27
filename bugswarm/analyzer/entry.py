import getopt
import logging
import sys

from bugswarm.analyzer.analyzer import Analyzer
from bugswarm.common import log
from bugswarm.common.utils import get_current_component_version_message


def main(argv=None):
    argv = argv or sys.argv

    # Configure logging.
    log.config_logging(getattr(logging, 'INFO', None))

    # Log the current version of this BugSwarm component.
    log.info(get_current_component_version_message('Analyzer'))

    mode, reproduced, orig, log_filename, print_result, job_id, build_system, trigger_sha, repo, mining =\
        _validate_input(argv)

    analyzer = Analyzer()
    if mode == 0:
        analyzer.compare_single_log(reproduced, orig, job_id, build_system, trigger_sha, repo, print_result,
                                    mining=mining)
    elif mode == 1:
        analyzer.analyze_single_log(log_filename, job_id, build_system, trigger_sha, repo, print_result, mining=mining)
    else:
        raise Exception('Unsupported mode: {}.'.format(mode))


def _validate_input(argv):
    shortopts = 'r:o:l:j:b:t:'
    longopts = 'reproduced= orig= log= job_id= build_system= trigger_sha= repo= mining= print '.split()
    mode = -1
    reproduced = None
    orig = None
    log_filename = None
    print_result = False
    job_id = None
    build_system = None
    trigger_sha = None
    repo = None
    mining = True

    try:
        optlist, args = getopt.getopt(argv[1:], shortopts, longopts)
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in optlist:
        if opt in ('-r', '--reproduced_log'):
            reproduced = arg
        if opt in ('-o', '--orig_log'):
            orig = arg
        if opt in ('-l', '--log'):
            log_filename = arg
        if opt in ('-j', '--job_id'):
            job_id = arg
        if opt in ('-b', '--build_system'):
            build_system = arg
        if opt in ('-t', '--trigger_sha'):
            trigger_sha = arg
        if opt == '--repo':  # repo slug
            repo = arg
        if opt == '--print':
            print_result = True
        if opt == '--mining':
            mining = False if arg.lower() in ['0', 'off', 'false'] else True

    if reproduced and orig:
        if job_id and '.log' in reproduced and '.log' in orig:
            mode = 0
    elif job_id and not reproduced and not orig:
        if log_filename:
            mode = 1
    else:
        print_usage()
        sys.exit(2)
    return mode, reproduced, orig, log_filename, print_result, job_id, build_system, trigger_sha, repo, mining


def print_usage():
    log.info('Analyzer Usage:')
    log.info('-----------------------------------------------------------------------')
    log.info('To analyze compare reproduced log with original Travis log:')
    log.info('    Python')
    log.info('      Example: python3 entry.py -r 45123523.log -o 45123523-orig.log -j 45123523')
    log.info('    Java')
    log.info('      Example: python3 entry.py -r 308408479.log -o 308408479-orig.log -j 308408479 -b maven')
    log.info('      Example: python3 entry.py -r 308408479.log -o 308408479-orig.log -j 308408479 -t 67bc28d1a4fe777b50'
             '35f331da02ba2db2c682a6 --repo=Adobe-Consulting-Services/acs-aem-commons')
    log.info('To analyze a log:')
    log.info('    Python')
    log.info('      Example: python3 entry.py -l 23434234.log -j 23434234')
    log.info('    Java')
    log.info('      Example: python3 entry.py -l 308408479.log -j 308408479 -b maven')
    log.info('      Example: python3 entry.py -l 308408479.log -j 308408479 -t 67bc28d1a4fe777b5035f331da02ba2db2c682a6'
             ' --repo=Adobe-Consulting-Services/acs-aem-commons')
    log.info('{:<30}{:<30}'.format('-r, --reproduced_log', 'path of log, path should end with .log'))
    log.info('{:<30}{:<30}'.format('-o, --orig_log', 'path of log, path should end with .log'))
    log.info('{:<30}{:<30}'.format('-l, --log', 'path of log, path should end with .log'))
    log.info('{:<30}{:<30}'.format('-j, --job_id', 'job id of the log'))
    log.info('{:<30}{:<30}'.format('-b, --build_system', 'build system of the project'))
    log.info('{:<30}{:<30}'.format('-t, --trigger_sha', 'trigger sha for log'))
    log.info('{:<30}{:<30}'.format('--repo', 'repository of the project'))
    log.info('{:<30}{:<30}'.format('--mining', 'use false to turn off mining mode, default is on.'))


if __name__ == '__main__':
    sys.exit(main())
