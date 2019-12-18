from kf_model_fhir import loader, cli
from conftest import TEST_DATA_DIR, PROFILE_DIR, RESOURCE_DIR
import os
import shutil

import pytest
from click.testing import CliRunner
runner = CliRunner()


@pytest.mark.parametrize(
    'path, expected_exc',
    [
        (os.path.join(PROFILE_DIR, 'StructureDefinition-Participant.json'),
         None)
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


def test_add_resource_to_ig(temp_ig):
    """
    Test kf_model_fhir.app.add_resource_to_ig
    """
    runner = CliRunner()
    temp_site_root = temp_ig
    temp_ig_control_file = os.path.join(temp_site_root, 'ig.json')

    # Add conformance resource and example resources to IG
    files = ['profiles/extensions/StructureDefinition-proband-status.json',
             'profiles/StructureDefinition-Participant.json',
             'resources/participant-example.json']
    for f in files:
        source = os.path.join(TEST_DATA_DIR, f)
        opts = ['--ig_control_file', temp_ig_control_file,
                '--is_example']
        filename = os.path.split(f)[-1]
        if f.startswith('profiles'):
            dest = os.path.join(
                temp_site_root, 'source', 'resources', filename
            )
            opts.pop()
        else:
            dest = os.path.join(temp_site_root, 'source', 'examples', filename)
        shutil.copyfile(source, dest)
        result = runner.invoke(cli.add, [dest] + opts)

        # Check output
        assert result.exit_code == 0

    # Validate IG
    result = runner.invoke(
        cli.validate,
        [temp_ig_control_file, '--publisher_opts', '-tx n/a']
    )
    assert result.exit_code == 0


def test_invalid_ig(temp_ig):
    """
    Make sure invalid IG fails validation
    """
    runner = CliRunner()
    temp_site_root = temp_ig
    temp_ig_control_file = os.path.join(temp_site_root, 'ig.json')

    # Add invalid conformance resources
    invalid_profile_dir = os.path.join(PROFILE_DIR, 'invalid')
    for fn in os.listdir(invalid_profile_dir):
        src = os.path.join(PROFILE_DIR, 'invalid', fn)
        dst = os.path.join(temp_site_root, 'source', 'resources', fn)
        shutil.copyfile(src, dst)
        result = runner.invoke(
            cli.add, [dst, '--ig_control_file', temp_ig_control_file]
        )
        assert result.exit_code == 0

    # Add invalid example resources
    invalid_example_dir = os.path.join(RESOURCE_DIR, 'invalid')
    if os.path.exists(invalid_example_dir):
        for fn in os.listdir(invalid_profile_dir):
            src = os.path.join(PROFILE_DIR, 'invalid', fn)
            dst = os.path.join(temp_site_root, 'source', 'examples', fn)
            shutil.copyfile(src, dst)
            result = runner.invoke(
                cli.add,
                [dst, '--is_example',
                 '--ig_control_file', temp_ig_control_file]
            )
            assert result.exit_code == 0

    # Validate IG
    result = runner.invoke(
        cli.validate,
        [temp_ig_control_file, '--publisher_opts', '-tx n/a']
    )
    assert result.exit_code != 0
