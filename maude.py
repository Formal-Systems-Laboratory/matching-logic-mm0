import subprocess
from shutil import which

def maude_path() -> str:
    if which('maude') is not None:
        return 'maude'
    return './maude/maude'
    

def check_maude_version() -> None:
    from packaging import version
    expected_version = version.parse('3.2.1')
    actual_version = version.parse(subprocess.check_output([maude_path(), '--version'], text=True))
    assert actual_version >=  expected_version, "Expected Maude version '{}' or greater in PATH, got '{}'".format(expected_version, actual_version)

def reduce_in_module(src: str, module: str, expected_sort: str, term: str) -> str:
    command = [maude_path(), '-no-banner', '-no-wrap', '-batch', src]
    input = 'reduce in {0} : {1} . \n'.format(module, term)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output_str, err_output_str = process.communicate(input=input)
    if process.returncode != 0:
        err_msg = "Maude exited with code: {} \n\nstderr:\n===========\n{}\n\nstdout\n===========\n{}\n".format(process.returncode, output_str, err_output_str)
        raise Exception(err_msg)
    elif len(err_output_str):
        err_msg = "Maude produced warnings: {} \n\nstderr:\n===========\n{}\n\nstdout\n===========\n{}\n".format(process.returncode, output_str, err_output_str)
        raise Exception(err_msg)

    output = output_str.split('\n')

    # Sanity check
    assert(output[0] == '=========================================='), output
    assert(output[1].startswith('reduce in {0}'.format(module))), output
    assert(output[2].startswith('rewrites: ')), output
    assert(output[-2:] == ['Bye.', '']), output

    # Parsing
    output = output[3:-2]
    result_string = 'result {0}: '.format(expected_sort)
    assert(output[0].startswith(result_string)), '\n'.join(output)
    output[0] = output[0][len(result_string):]
    return '\n'.join(output)

