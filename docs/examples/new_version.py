import typing as t
import arc
from arc import types


def greater_than_previous(value: types.SemVer, ctx: arc.Context):
    current_version: types.SemVer | None = ctx.state.get("curr_version")
    if not current_version:
        return value

    if current_version >= value:
        raise arc.ValidationError(
            f"New version must be greater than current version ({current_version})"
        )

    return value


NewVersion = t.Annotated[types.SemVer, greater_than_previous]


@arc.command
def command(version: NewVersion):
    arc.print(version)


command(state={"curr_version": types.SemVer.parse("1.0.0")})
