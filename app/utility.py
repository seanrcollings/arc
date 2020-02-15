from app.cli import CLI

class Utility(CLI):
    '''
        CLI Helper class
        Wrapper to create a group of utility functions

        When a utility is registered with the CLI, each of
        the utility's commands are added to the CLI's commands,
        with the utility's name preprended to them
        Examlple:
            Utility db
            db:create
            db:drop
            db:createuser
    '''
    def __init__(self, name):
        self.name = name
        self.scripts = {}

    def __repr__(self):
        return "Utility"

    def __call__(self, command, options):
        if command not in self.scripts:
            print("That command does not exist")
            return

        script = self.scripts[command]
        if script['options'] is None:
            self.scripts[command]['function']()
        else:
            self.scripts[command]['function'](
                **self.arguements_dict(script, options))


    def helper(self):
        '''
        Helper function
        '''
        print(f"Utility {self.name}")
        for script, value in self.scripts.items():
            helper = value['function'].__doc__.strip('\n')
            name = format(script)
            print(f":{name}")
            print(helper)