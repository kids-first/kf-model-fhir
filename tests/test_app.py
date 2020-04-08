import os

import pytest
from click.testing import CliRunner

from kf_model_fhir import loader, cli, app
from conftest import (
    PROFILE_DIR,
    EXAMPLE_DIR,
    EXTENSION_DIR,
    INVALID_RESOURCES,
    copy_resources_into_ig
)

from pprint import pprint

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
    copy_resources_into_ig(dir_list, temp_site_root)

    # Validate IG
    result = runner.invoke(
        cli.validate,
        [temp_ig_control_file, '--publisher_opts', '-tx n/a', '--clear_output']
    )
    assert result.exit_code == expected_code


@pytest.mark.parametrize(
    "resource_dict, error_msg",
    INVALID_RESOURCES
)
def test_custom_validate(resource_dict, error_msg):
    """
    Test kf_model_fhir.app._custom_validate
    """
    with pytest.raises(Exception) as e:
        app._custom_validate([resource_dict])
    assert error_msg in str(e.value)


@pytest.mark.parametrize(
    'filepath, error_msg',
    [
        (os.path.join(
            PROFILE_DIR, 'invalid', 'StructureDefinition-Participant.json'
        ), 'All resources must have an `id` attribute'),
        (os.path.join(
            EXAMPLE_DIR, 'invalid', 'Patient-pt-001.json'
        ), 'Resource file names must follow pattern')
    ]
)
def test_update_ig(debug_caplog, filepath, error_msg):
    # Run add command
    runner = CliRunner()
    result = runner.invoke(cli.add, [filepath])
    assert result.exit_code != 0
    assert error_msg in debug_caplog.text


def test_remove_old_ig_state(temp_site_root):
    """
    Tests that old state in IG configuration is properly removed
    """
    def resource_files_in_ig(ig_control_filepath):
        ig = app._load_ig_resource_dict(ig_control_filepath)
        resources = ig['content']['definition']['resource']
        return set([
            r['reference']['reference'].replace('/', '-') + '.json'
            for r in resources
        ])

    # Add profiles and extensions to IG
    profiles_dir = os.path.join(PROFILE_DIR, 'valid')
    ext_dir = os.path.join(EXTENSION_DIR, 'valid')
    filepaths = copy_resources_into_ig(
        [profiles_dir, ext_dir], temp_site_root
    )
    ig_control_filepath = os.path.join(temp_site_root, 'ig.ini')
    runner = CliRunner()
    result = runner.invoke(
        cli.add,
        [
            os.path.join(temp_site_root, 'input', 'resources'),
            '--ig_control_file',
            ig_control_filepath
        ]
    )
    assert result.exit_code == 0

    # Files referenced in IG should be the supplied profiles and extensions
    ig_filenames = resource_files_in_ig(ig_control_filepath)
    filenames = set([os.path.split(fp)[-1] for fp in filepaths])
    assert ig_filenames == filenames

    # Add only extensions to IG
    # Old state = profiles which should be removed from IG config
    result = runner.invoke(
        cli.add,
        [
            os.path.join(temp_site_root, 'input', 'resources', 'extensions'),
            '--ig_control_file',
            ig_control_filepath
        ]
    )
    # Files referenced by IG should only be the supplied extensions
    ig_filenames = resource_files_in_ig(ig_control_filepath)
    extension_filenames = set([fn for fn in os.listdir(ext_dir)])
    assert ig_filenames == extension_filenames
