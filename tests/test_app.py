from kf_model_fhir import loader, cli
from conftest import (
    PROFILE_DIR,
    EXAMPLE_DIR,
    EXTENSION_DIR
)
import os
import shutil

import pytest
from click.testing import CliRunner

VALID_PROFILE_DIR = os.path.join(PROFILE_DIR, 'valid')
VALID_PROFILES = [os.path.join(VALID_PROFILE_DIR, f)
                  for f in os.listdir(VALID_PROFILE_DIR)]


@pytest.mark.parametrize(
    'path, expected_exc',
    [
        (VALID_PROFILES[0], None)
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
          os.path.join(EXAMPLE_DIR, 'valid'),
          os.path.join(EXTENSION_DIR, 'valid')], 0),
        ([os.path.join(PROFILE_DIR, 'invalid'),
          os.path.join(EXAMPLE_DIR, 'invalid')], 1),
    ],
)
def test_ig_validation(temp_site_root, dir_list, expected_code):
    """
    Test kf_model_fhir.app.validate
    """
    runner = CliRunner()
    temp_ig_control_file = os.path.join(temp_site_root, 'ig.ini')

    # Add conformance resource and example resources to IG
    filepaths = [os.path.join(d, f) for d in dir_list for f in os.listdir(d)]
    for source in filepaths:
        path_parts = os.path.split(source)
        if not os.path.isfile(source):
            continue
        filename = path_parts[-1]
        dest_dir = os.path.join(
            temp_site_root, 'input', 'resources',
            path_parts[0].split('/')[-2]
        )
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, filename)
        # Copy test file into temp IG
        shutil.copyfile(source, dest)

    # Validate IG
    result = runner.invoke(
        cli.validate,
        [temp_ig_control_file, '--publisher_opts', '-tx n/a', '--clear_output']
    )
    assert result.exit_code == expected_code
