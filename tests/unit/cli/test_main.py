import argparse
import os
import unittest.mock

import pytest

from nomad.cli.main import main, Nomad
from nomad.cli.project import get_project
from nomad.conf.exceptions import ConfigError
from nomad.container import Container
from nomad.exceptions import NomadException
from nomad.project import Project


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


def _gen_argparse_namespace(**kwargs):
    default_options = {
        'action': None,
        'force': False,
        'name': None,
        'subcommand': None,
        'verbose': False,
    }
    default_options.update(kwargs)
    return argparse.Namespace(**default_options)


@unittest.mock.patch(
    'argparse.ArgumentParser.parse_args', return_value=_gen_argparse_namespace(action='help'))
@unittest.mock.patch.object(Nomad, 'help')
def test_main_function_can_run_a_nomad_command(mock_help_action, mock_parse_args):
    main()
    assert mock_help_action.call_count == 1


class TestNomad:
    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='destroy'))
    @unittest.mock.patch('builtins.input', return_value='Y')
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'destroy')
    @unittest.mock.patch.object(Container, 'exists')
    def test_can_run_the_destroy_action_for_all_containers_of_a_project(
            self, container_exists_mock, mock_project_destroy, mock_project, y_mock,
            mock_parse_args):
        container_exists_mock.__get__ = unittest.mock.Mock(return_value=True)
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_destroy.call_count == 1
        assert mock_project_destroy.call_args == [{'container_names': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='destroy', name=['default', ]))
    @unittest.mock.patch('builtins.input', return_value='Y')
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'destroy')
    @unittest.mock.patch.object(Container, 'exists')
    def test_can_run_the_destroy_action_for_specific_containers(
            self, container_exists_mock, mock_project_destroy, mock_project, y_mock,
            mock_parse_args):
        container_exists_mock.__get__ = unittest.mock.Mock(return_value=True)
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_destroy.call_count == 1
        assert mock_project_destroy.call_args == [{'container_names': ['default', ], }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='destroy', force=True))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'destroy')
    @unittest.mock.patch.object(Container, 'exists')
    def test_can_run_the_destroy_containers_using_a_force_option(
            self, container_exists_mock, mock_project_destroy, mock_project, mock_parse_args):
        container_exists_mock.__get__ = unittest.mock.Mock(return_value=True)
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_destroy.call_count == 1
        assert mock_project_destroy.call_args == [{'container_names': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='destroy'))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'destroy')
    @unittest.mock.patch.object(Container, 'exists')
    def test_can_force_the_destroy_action_if_the_containers_do_not_exist(
            self, container_exists_mock, mock_project_destroy, mock_project, mock_parse_args):
        container_exists_mock.__get__ = unittest.mock.Mock(return_value=False)
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_destroy.call_count == 1
        assert mock_project_destroy.call_args == [{'container_names': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='halt'))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'halt')
    def test_can_run_the_halt_action_for_all_containers_of_a_project(
            self, mock_project_halt, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_halt.call_count == 1
        assert mock_project_halt.call_args == [{'container_names': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='halt', name=['c1', 'c2', ]))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'halt')
    def test_can_run_the_halt_action_for_specific_containers(
            self, mock_project_halt, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_halt.call_count == 1
        assert mock_project_halt.call_args == [{'container_names': ['c1', 'c2', ], }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='help'))
    def test_can_print_the_global_help(self, mock_parse_args):
        n = Nomad()
        assert n._parsers['main'].parse_args().subcommand is None

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='help', subcommand='up'))
    def test_can_print_the_help_for_a_specific_subcommand(self, mock_parse_args):
        n = Nomad()
        assert n._parsers['main'].parse_args().subcommand == 'up'

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='provision'))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'provision')
    def test_can_run_the_provision_action_for_all_containers_of_a_project(
            self, mock_project_provision, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_provision.call_count == 1
        assert mock_project_provision.call_args == [{'container_names': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='provision', name=['c1', 'c2', ]))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'provision')
    def test_can_run_the_provision_action_for_specific_containers(
            self, mock_project_provision, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_provision.call_count == 1
        assert mock_project_provision.call_args == [{'container_names': ['c1', 'c2', ], }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='shell'))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'shell')
    def test_can_run_the_shell_action_for_all_containers_of_a_project(
            self, mock_project_shell, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_shell.call_count == 1
        assert mock_project_shell.call_args == [{'container_name': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='shell', name=['c1', ]))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'shell')
    def test_can_run_the_shell_action_for_a_specific_container(
            self, mock_project_shell, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_shell.call_count == 1
        assert mock_project_shell.call_args == [{'container_name': ['c1', ], }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='status'))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'status')
    def test_can_run_the_status_action_for_all_containers_of_a_project(
            self, mock_project_status, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_status.call_count == 1
        assert mock_project_status.call_args == [{'container_names': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='status', name=['c1', 'c2', ]))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'status')
    def test_can_run_the_status_action_for_specific_containers(
            self, mock_project_status, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_status.call_count == 1
        assert mock_project_status.call_args == [{'container_names': ['c1', 'c2', ], }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='up'))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'up')
    def test_can_run_the_up_action_for_all_containers_of_a_project(
            self, mock_project_up, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_up.call_count == 1
        assert mock_project_up.call_args == [{'container_names': None, }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='up', name=['c1', 'c2', ], verbose=True))
    @unittest.mock.patch.object(Nomad, 'project')
    @unittest.mock.patch.object(Project, 'up')
    def test_can_run_the_up_action_for_specific_containers(
            self, mock_project_up, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(
            return_value=get_project(os.path.join(FIXTURE_ROOT, 'project01')))
        Nomad()
        assert mock_project_up.call_count == 1
        assert mock_project_up.call_args == [{'container_names': ['c1', 'c2', ], }, ]

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace())
    def test_exit_if_no_action_is_provided(self, mock_parse_args):
        with pytest.raises(SystemExit):
            Nomad()

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=_gen_argparse_namespace(action='help', subcommand='unknown'))
    def test_exit_if_a_cli_error_is_encountered(self, mock_parse_args):
        with pytest.raises(SystemExit):
            Nomad()

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args', return_value=_gen_argparse_namespace(action='up'))
    @unittest.mock.patch.object(Nomad, 'project')
    def test_exit_if_a_config_error_is_encountered(self, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(side_effect=ConfigError(msg='TEST'))
        with pytest.raises(SystemExit):
            Nomad()

    @unittest.mock.patch(
        'argparse.ArgumentParser.parse_args', return_value=_gen_argparse_namespace(action='up'))
    @unittest.mock.patch.object(Nomad, 'project')
    def test_exit_if_a_nomad_error_is_encountered(self, mock_project, mock_parse_args):
        mock_project.__get__ = unittest.mock.Mock(side_effect=NomadException(msg='TEST'))
        with pytest.raises(SystemExit):
            Nomad()
