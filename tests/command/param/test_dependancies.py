from typing import Annotated
import pytest
import arc
from arc import errors


class DependableType:
    @classmethod
    def __depends__(self, ctx: arc.Context):
        return "DependableType"


class TestTypeDependancies:
    def test_depends(self):
        @arc.command()
        def command(val: DependableType):
            return val

        assert command("") == "DependableType"
        assert len(list(command.injected_params)) == 1

    def test_no_default(self):
        with pytest.raises(errors.ParamError):

            @arc.command()
            def command(val: DependableType = arc.Argument()):
                return val

        with pytest.raises(errors.ParamError):

            @arc.command()
            def command(val: DependableType = 1):  # type: ignore
                return val

    def test_annotation(self):
        @arc.command()
        def command(val: Annotated[DependableType, 1]):
            return val

        assert command("") == "DependableType"


def dep1(ctx):
    return 1


def dep2(ctx):
    return 2


class TestParamDependancies:
    def test_depends(self):
        @arc.command()
        def command(val=arc.Depends(dep1)):
            return val

        assert len(list(command.injected_params)) == 1
        assert command("") == 1

        with pytest.raises(errors.UnrecognizedArgError):
            command("val")

    def test_multiple_depends(self):
        @arc.command()
        def command(val=arc.Depends(dep1), val2=arc.Depends(dep2)):
            return val, val2

        assert len(list(command.injected_params)) == 2
        assert command("") == (1, 2)

        with pytest.raises(errors.UnrecognizedArgError):
            command("val val2")
