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
    def __init__(self, name, context_manager=None):
        self.name = name
        self.scripts = {}
        self.context_manger = context_manager

    def __repr__(self):
        return "Utility"

    def __call__(self, command, options):
        self.execute(command, options)

    def helper(self):
        '''
        Helper function
        '''
        print(f"\nUtility {self.name}")
        if len(self.scripts) > 0:
            for script, value in self.scripts.items():
                helper = "\tNo Docstring"
                if ( doc := value['function'].__doc__) is not None:
                    helper = doc.strip('\n')

                name = format(script)
                print(f":{name}")
                print(helper)
        else:
            print("No scripts defined")