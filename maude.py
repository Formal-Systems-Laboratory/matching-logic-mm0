import subprocess

def check_maude_version() -> None:
    from packaging import version
    expected_version = version.parse('3.2.1')
    actual_version = version.parse(subprocess.check_output(['maude', '--version'], text=True))
    assert actual_version >=  expected_version, "Expected Maude version '{}' or greater in PATH, got '{}'".format(expected_version, actual_version)

def reduce_in_module(src: str, module: str, expected_sort: str, term: str) -> str:
    output_str = subprocess.check_output(
        ['maude', '-no-banner', '-no-wrap', '-batch', src],
        input='reduce in {0} : {1} . \n'.format(module, term),
        text=True
    )
    output = output_str.split('\n')

    # Sanity check
    assert(output[0] == '=========================================='), output
    assert(output[1].startswith('reduce in {0}'.format(module)))
    assert(output[2].startswith('rewrites: '))
    assert(output[-2:] == ['Bye.', ''])
    output = output[3:-2]

    result_string = 'result {0}: '.format(expected_sort)
    assert(output[0].startswith(result_string)), output[0]

    output[0] = output[0][len(result_string):]
    return '\n'.join(output)

