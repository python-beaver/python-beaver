from beaver.worker import run_worker


def cli(method, options):

    if method == "worker":
        run_worker(options)
    else:
        from IPython.Shell import IPythonShellEmbed
        ipshell = IPythonShellEmbed([])
        ipshell()
