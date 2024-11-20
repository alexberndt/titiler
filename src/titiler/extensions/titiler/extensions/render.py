"""rio-stac render Extension."""

from typing import Dict

from attrs import define
from fastapi import Depends, Query
from typing_extensions import Annotated

from titiler.core.factory import FactoryExtension, MultiBaseTilerFactory


@define
class renderExtension(FactoryExtension):
    """Add /render endpoint to a COG TilerFactory."""

    def register(self, factory: MultiBaseTilerFactory):
        """Register endpoint to the tiler factory."""

        @factory.router.get(
            "/renders", response_model=Dict, name="Show STAC item render options"
        )
        def renders(src_path=Depends(factory.path_dependency)):
            """Show render options for STAC item."""
            with factory.reader(src_path) as src:
                renders = src.item.properties.get("renders", {})

                # Create query from

                return {"renders": renders}

        @factory.router.get(
            "/render", response_model=Dict, name="Get URL for render type"
        )
        def render(
            render_name: Annotated[
                str,
                Query(description="render name for the source."),
            ],
            src_path=Depends(factory.path_dependency),
        ):
            """Return URL for a render item."""
            with factory.reader(src_path) as src:
                renders = src.item.properties.get("renders", {})
                if len(renders) == 0:
                    return "no renders in provided item"
                if render_name not in renders:
                    return f"render {render_name} not found"

                render = renders[render_name]

                # read render details from payload
                params = []

                if "assets" in render:
                    params.append(f"assets={','.join(render['assets'])}")
                if "rescale" in render:
                    params.append(
                        f"rescale={','.join([str(limit) for band in render['rescale'] for limit in band])}"
                    )
                if "resampling" in render:
                    params.append(f"resmapling={render['resampling']}")

                prefix = "https://api.cogeo.xyz/stac/crop/14.869,37.682,15.113,37.862/256x256.png"

                return {"url": f"{prefix}?url={src_path}&{'&'.join(params)}"}
