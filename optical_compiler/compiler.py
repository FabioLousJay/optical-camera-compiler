"""Core OpticalCompiler coordinator."""

from __future__ import annotations

from typing import Any, Optional, Union

from .adapters import get_adapter
from .models import (
    CameraProfile,
    CompiledPayload,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from .profiles import apply_overrides, load_profile


class OpticalCompiler:
    """Deterministic compiler translating scene intent into physically-grounded optical prompts."""

    def __init__(self, profile: Union[str, CameraProfile] = "phase_one_iq4") -> None:
        """Initialize compiler with a base camera profile.

        Args:
            profile: Profile name (e.g. 'phase_one_iq4'), file path, or CameraProfile object.
        """
        if isinstance(profile, CameraProfile):
            self.base_profile = profile
        else:
            self.base_profile = load_profile(profile)

    def compile(
        self,
        scene: Union[str, SceneInput],
        target: Union[str, TargetEngine] = TargetEngine.FLUX,
        *,
        framing: Optional[str] = None,
        environment: Optional[str] = None,
        wardrobe: Optional[str] = None,
        mood: Optional[str] = None,
        aperture: Optional[str] = None,
        lens: Optional[str] = None,
        lighting: Optional[str] = None,
        aspect_ratio: str = "4:5",
        film_stock: Optional[str] = None,
        optical_filter: Optional[str] = None,
        shutter_speed: Optional[str] = None,
        lighting_modifier: Optional[str] = None,
        custom_positives: Optional[list[str]] = None,
        custom_negatives: Optional[list[str]] = None,
        reference: Optional[Union[ReferenceImageInput, dict[str, Any]]] = None,
    ) -> CompiledPayload:
        """Compile a scene description into a model-specific, zero-artifact prompt payload.

        Args:
            scene: Plain text description of the subject/scene, or a pre-configured SceneInput.
            target: Target diffusion engine ('imagen', 'flux', 'sdxl', 'midjourney', 'raw').
            framing: Optional framing (e.g. 'tight macro portrait', 'three-quarter editorial').
            environment: Optional environment/background description.
            wardrobe: Optional styling and wardrobe description.
            mood: Optional mood and atmosphere.
            aperture: Override lens aperture (e.g. 'f/4', 'f/2.8').
            lens: Override lens model (e.g. 'Schneider Kreuznach 150mm LS f/3.5').
            lighting: Override lighting setup.
            aspect_ratio: Aspect ratio (default '4:5').
            film_stock: Film stock or sensor color science (e.g. 'Kodak Portra 400', 'Cinestill 800T').
            optical_filter: Optical diffusion or polarizer (e.g. 'Tiffen Black Pro-Mist 1/8').
            shutter_speed: Shutter speed or motion cadence.
            lighting_modifier: Specific lighting modifier (e.g. 'Broncolor Para 220').
            custom_positives: Additional positive tokens.
            custom_negatives: Additional negative tokens.

        Returns:
            CompiledPayload with positive prompt, negative prompt, parameters, and metadata.
        """
        # 1. Normalize ReferenceInput if provided
        ref_obj: Optional[ReferenceImageInput] = None
        if isinstance(reference, ReferenceImageInput):
            ref_obj = reference
        elif isinstance(reference, dict):
            mode_val = reference.get("mode")
            mode = (
                mode_val
                if isinstance(mode_val, ReferenceMode)
                else ReferenceMode.from_str(str(mode_val))
            )
            ref_obj = ReferenceImageInput(
                filename=reference.get("filename"),
                file_path=reference.get("file_path"),
                data_uri=reference.get("data_uri"),
                mode=mode,
                denoise_strength=float(reference.get("denoise_strength", 0.35)),
                fidelity_lock=float(reference.get("fidelity_lock", 0.95)),
                detected_aspect_ratio=reference.get("detected_aspect_ratio"),
                subject_description=reference.get("subject_description"),
                preserved_elements=reference.get(
                    "preserved_elements",
                    [
                        "facial geometry",
                        "eye structure and gaze",
                        "facial bone structure",
                        "biometric identity",
                        "anatomical proportions",
                    ],
                ),
            )

        # 2. Normalize SceneInput
        if isinstance(scene, str):
            scene_input = SceneInput(
                subject=scene.strip(),
                framing=framing,
                environment=environment,
                wardrobe=wardrobe,
                mood=mood,
                aperture=aperture,
                lens=lens,
                lighting=lighting,
                aspect_ratio=aspect_ratio,
                film_stock=film_stock,
                optical_filter=optical_filter,
                shutter_speed=shutter_speed,
                lighting_modifier=lighting_modifier,
                custom_positives=custom_positives or [],
                custom_negatives=custom_negatives or [],
                reference=ref_obj,
            )
        else:
            scene_input = scene
            # Apply any explicit kwargs on top of the SceneInput object
            if framing:
                scene_input.framing = framing
            if environment:
                scene_input.environment = environment
            if wardrobe:
                scene_input.wardrobe = wardrobe
            if mood:
                scene_input.mood = mood
            if aperture:
                scene_input.aperture = aperture
            if lens:
                scene_input.lens = lens
            if lighting:
                scene_input.lighting = lighting
            if aspect_ratio != "4:5":
                scene_input.aspect_ratio = aspect_ratio
            if film_stock:
                scene_input.film_stock = film_stock
            if optical_filter:
                scene_input.optical_filter = optical_filter
            if shutter_speed:
                scene_input.shutter_speed = shutter_speed
            if lighting_modifier:
                scene_input.lighting_modifier = lighting_modifier
            if custom_positives:
                scene_input.custom_positives.extend(custom_positives)
            if custom_negatives:
                scene_input.custom_negatives.extend(custom_negatives)
            if ref_obj:
                scene_input.reference = ref_obj

        # 3. Parse target engine
        engine = (
            target
            if isinstance(target, TargetEngine)
            else TargetEngine.from_str(target)
        )

        # 3. Apply overrides to active profile
        active_profile = apply_overrides(self.base_profile, scene_input)

        # 4. Compile via target adapter
        adapter = get_adapter(engine)
        return adapter.compile(scene_input, active_profile)

    def compile_all(
        self,
        scene: Union[str, SceneInput],
        **kwargs: Any,
    ) -> dict[str, CompiledPayload]:
        """Compile the scene across all registered generation targets at once."""
        results = {}
        for engine in [
            TargetEngine.IMAGEN,
            TargetEngine.FLUX,
            TargetEngine.SDXL,
            TargetEngine.MIDJOURNEY,
        ]:
            results[engine.value] = self.compile(scene, target=engine, **kwargs)
        return results
