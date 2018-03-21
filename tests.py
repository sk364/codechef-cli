import unittest

from codechefcli import __main__ as entry_point


class ScriptTests(unittest.TestCase):
    def test_main(self):
        """
        :desc: Test to check if `__main__.main` method is behaving
               correctly when receiving incorrect number of arguments.
        """

        with self.assertRaises(SystemExit):
            entry_point.main(['codechefcli', '--problem'])

    def test_create_parser(self):
        """
        :desc: Test to check if a valid parser object is returned or
               not by `__main__.create_parser` method.
        """

        parser = entry_point.create_parser()
        args = parser.parse_args(['--problem', 'WEICOM'])
        self.assertEqual(args.problem, 'WEICOM')
 
