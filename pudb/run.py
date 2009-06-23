def main():
    import sys

    from optparse import OptionParser
    parser = OptionParser(
            usage="usage: %prog [options] SCRIPT-TO-RUN [SCRIPT-ARGUMENTS]")

    parser.add_option("-s", "--steal-output", action="store_true"),
    parser.add_option("--pre-run", metavar="COMMAND",
            help="Run command before each program run")
    parser.disable_interspersed_args()
    options, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(2)

    mainpyfile =  args[0]
    from os.path import exists, dirname
    if not exists(mainpyfile):
        print 'Error:', mainpyfile, 'does not exist'
        sys.exit(1)

    sys.argv = args

    # Replace pudb's dir with script's dir in front of module search path.
    sys.path[0] = dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. The best approach would be to
    # have a "restart" command which would allow explicit specification of
    # command line arguments.

    from pudb.debugger import Debugger
    dbg = Debugger(steal_output=options.steal_output)

    while True:
        if options.pre_run:
            from subprocess import call
            retcode = call(options.pre_run, close_fds=True, shell=True)
            if retcode:
                print "*** WARNING: pre-run process exited with code %d." % retcode
            pre_run_msg = ("\n\nIf you decide to restart, '%s' will be run prior to "
                    "actually restarting." % options.pre_run)
        else:
            pre_run_msg = ""

        status_msg = ""

        try:
            dbg._runscript(mainpyfile)
        except SystemExit, se:
            status_msg = "The debuggee exited normally with status code was %d.\n\n" % se.code
        except:
            dbg.post_mortem = True
            dbg.interaction(None, sys.exc_info())

        import urwid
        result = dbg.ui.call_with_ui(dbg.ui.dialog,
            urwid.ListBox([urwid.Text(
                ("Your PuDB session has ended.\n\n%s"
                "Would you like to quit PuDB or restart your program?"
                % status_msg)+pre_run_msg)]),
            [
                ("Restart", "restart"),
                ("Quit", "quit"),
                ],
            focus_buttons=True,
            bind_enter_esc=False,
            title="Finished")

        if result == "quit":
            return

        dbg.restart()



if __name__=='__main__':
    main()
