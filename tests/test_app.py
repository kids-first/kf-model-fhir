from kf_model_fhir import loader, cli
from conftest import PROFILE_DIR, RESOURCE_DIR
import os
import shutil

import pytest
from click.testing import CliRunner
runner = CliRunner()

valid_profiles = [os.path.join(PROFILE_DIR, 'valid', f)
                  for f in os.listdir(os.path.join(PROFILE_DIR, 'valid'))]


@pytest.mark.parametrize(
    'path, expected_exc',
    [
        (valid_profiles[0], None)
    ]
)
def test_fhir_format(caplog, tmpdir, path, expected_exc):
    format_dict = {
        '.xml': 'json',
        '.json': 'xml'
    }
    # Input file -> to output file
    in_file_ext = os.path.splitext(path)[-1]
    output_format = format_dict[in_file_ext]
    out_file = os.path.join(tmpdir, 'out_file.' + output_format)

    output_str, out_file = loader.fhir_format(path,
                                              output_filepath=out_file,
                                              output_format=output_format,
                                              write_to_file=True)
    assert output_str
    assert os.path.isfile(out_file)

    # Reverse - Convert output file back to input file
    in_file_ext = os.path.splitext(out_file)[-1]
    output_format = format_dict[in_file_ext]
    in_dirname, in_filename = os.path.split(out_file)
    out_file_2 = os.path.join(in_dirname, 'out_file_2.' + output_format)

    output_str, _ = loader.fhir_format(out_file,
                                       output_filepath=out_file_2,
                                       output_format=output_format,
                                       write_to_file=True)
    assert output_str
    assert os.path.isfile(out_file_2)

    # Clean up
    os.remove(out_file)


@pytest.mark.parametrize(
    "dir_list, expected_code",
    [
        ([os.path.join(PROFILE_DIR, 'valid'),
          os.path.join(RESOURCE_DIR, 'valid'),
          os.path.join(PROFILE_DIR, 'extensions')], 0),
        ([os.path.join(PROFILE_DIR, 'invalid'),
          os.path.join(RESOURCE_DIR, 'invalid')], 1),
    ],
)
def test_ig_validation(temp_ig, dir_list, expected_code):
    """
    Test kf_model_fhir.app.add_resource_to_ig
    """
    runner = CliRunner()
    temp_site_root = temp_ig
    temp_ig_control_file = os.path.join(temp_site_root, 'ig.json')

    # Add conformance resource and example resources to IG
    filepaths = [os.path.join(d, f) for d in dir_list for f in os.listdir(d)]
    for source in filepaths:
        if not os.path.isfile(source):
            continue
        filename = os.path.split(source)[-1]
        opts = ['--ig_control_file', temp_ig_control_file,
                '--is_example']
        if 'profiles' in os.path.split(source)[0]:
            dest = os.path.join(
                temp_site_root, 'source', 'resources', filename
            )
            opts.pop()
        else:
            dest = os.path.join(temp_site_root, 'source', 'examples', filename)

        # Copy test file into temp IG
        shutil.copyfile(source, dest)
        result = runner.invoke(cli.add, [dest] + opts)

        # Check output
        assert result.exit_code == 0

    # Validate IG
    result = runner.invoke(
        cli.validate,
        [temp_ig_control_file, '--publisher_opts', '-tx n/a']
    )
    assert result.exit_code == expected_code


if __name__ == '__main__':
    test_ig_validation('boo', [os.path.join(PROFILE_DIR, 'valid'),
                               os.path.join(RESOURCE_DIR, 'valid'),
                               os.path.join(PROFILE_DIR, 'extensions')], 0)
