"""Core OpticalCompiler coordinator."""

from __future__ import annotations

from typing import Any, Optional, Union

from .adapters import get_adapter
from .models import (
    AdSafeZone,
    AnamorphicSqueeze,
    CameraProfile,
    CompiledPayload,
    ContentType,
    CopySpace,
    GoboPattern,
    GripModifier,
    GripType,
    IrisBladeCount,
    LightingRatio,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    StreakFlare,
    TargetEngine,
)
from .profiles import apply_overrides, auto_select_profile, load_profile


class OpticalCompiler:
    """Deterministic compiler translating scene intent into physically-grounded optical prompts."""

    def __init__(self, profile: Union[str, CameraProfile] = "phase_one_iq4") -> None:
        """Initialize compiler with a base camera profile or 'auto' router.

        Args:
            profile: Profile name (e.g. 'phase_one_iq4', 'auto'), file path, or CameraProfile object.
        """
        if isinstance(profile, CameraProfile):
            self.base_profile = profile
            self.is_auto = False
        elif profile == "auto":
            self.base_profile = None
            self.is_auto = True
        else:
            self.base_profile = load_profile(profile)
            self.is_auto = False

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
        sharpness_protocol: bool = True,
        output_resolution: Optional[str] = None,
        suppress_text_branding: bool = True,
        lighting_preset: Optional[str] = None,
        capture_mode: Optional[str] = None,
        human_skin_realism: bool = True,
        content_type: Optional[Union[str, ContentType]] = None,
        text_preservation: bool = True,
        camera_angle: Optional[str] = None,
        color_mode: Optional[str] = None,
        crowd_action: Optional[str] = None,
        product_crop: Optional[str] = None,
        sku_color: Optional[str] = None,
        cap_geometry: Optional[str] = None,
        label_kerning: Optional[str] = None,
        material_finish: Optional[str] = None,
        seam_geometry: Optional[str] = None,
        approval_gate_100pct: bool = True,
        hand_lock: bool = False,
        grip_type: Optional[Union[str, GripType]] = None,
        hand_details: Optional[str] = None,
        anamorphic: bool = False,
        anamorphic_squeeze: Optional[Union[str, AnamorphicSqueeze]] = None,
        streak_flare: Optional[Union[str, StreakFlare]] = None,
        iris_blades: Optional[Union[str, IrisBladeCount]] = None,
        gobo: Optional[Union[str, GoboPattern]] = None,
        grip_modifier: Optional[Union[str, GripModifier]] = None,
        lighting_ratio: Optional[Union[str, LightingRatio]] = None,
        copy_space: Optional[Union[str, CopySpace]] = None,
        ad_safe_zone: Optional[Union[str, AdSafeZone]] = None,
    ) -> CompiledPayload:
        """Compile a scene description into a model-specific, zero-artifact prompt payload.

        Args:
            scene: Plain text description of the subject/scene, or a pre-configured SceneInput.
            target: Target diffusion engine ('gpt_images', 'imagen', 'midjourney', 'flux', 'sdxl', 'raw').
            framing: Optional framing (e.g. 'tight macro portrait', 'three-quarter editorial').
            environment: Optional environment/background description.
            wardrobe: Optional styling and wardrobe description.
            mood: Optional mood and atmosphere.
            aperture: Override lens aperture (e.g. 'f/4', 'f/2.8').
            lens: Override lens model (e.g. 'Schneider Kreuznach 150mm LS f/3.5').
            lighting: Override lighting setup.
            aspect_ratio: Aspect ratio (default '4:5' or '9:11').
            film_stock: Film stock or sensor color science (e.g. 'Kodak Portra 400', 'Cinestill 800T').
            optical_filter: Optical diffusion or polarizer (e.g. 'Tiffen Black Pro-Mist 1/8').
            shutter_speed: Shutter speed or motion cadence.
            lighting_modifier: Specific lighting modifier (e.g. 'Broncolor Para 220').
            custom_positives: Additional positive tokens.
            custom_negatives: Additional negative tokens.
            reference: Reference image metadata and anti-drift settings.
            sharpness_protocol: Enforce near-eye focus lock, iris sharpness, and stability cues.
            output_resolution: Exact uncompressed output target (e.g. '12MP PNG, vertical 9:11').
            suppress_text_branding: Actively eliminate text, brand names, logos, and watermarks.
            lighting_preset: Master photographic lighting recipe.
            capture_mode: Camera discipline and sensor stability mode.
            human_skin_realism: Enforce human skin realism override protocol.
            content_type: Classification of image content (photograph, portrait, document_scan, etc.).
            text_preservation: Enforce exact OCR safety and text preservation rules.
            hand_lock: Enforce 5-point biomechanical hand and finger precision gate.
            grip_type: Physical contact grip geometry (pinch, wrap, palm support, etc.).
            hand_details: Specific hand/finger anatomical details.
            anamorphic_squeeze: Cinema anamorphic squeeze ratio (e.g. 2.0x, 1.33x, 1.5x).
            streak_flare: Chromatic streak flare coating (cyan_blue, warm_gold, neutral_silver, vintage_magenta).
            iris_blades: Lens aperture blade geometry shaping bokeh discs and starburst spikes.
            gobo: Optical pattern projection cookie (venetian_blinds, dappled_foliage, etc.).
            grip_modifier: Professional studio grip modifier (beauty dish, butterfly 8x8 silk, snoot, floppy).
            lighting_ratio: Key-to-fill lighting contrast ratio (1:1, 2:1, 4:1, 8:1, 16:1).
            copy_space: Advertising negative copy space reservation (left, right, top, bottom third).
            ad_safe_zone: Digital and social advertising safe zone format.

        Returns:
            CompiledPayload with positive prompt, negative prompt, parameters, and metadata.
        """
        # 1. Normalize ReferenceInput if provided
        ref_obj: Optional[ReferenceImageInput] = None
        if isinstance(reference, ReferenceImageInput):
            ref_obj = reference
        elif isinstance(reference, dict):
            ref_obj = ReferenceImageInput(
                filename=reference.get("filename"),
                file_path=reference.get("file_path"),
                data_uri=reference.get("data_uri"),
                mode=ReferenceMode.from_str(reference.get("mode")),
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

        # Parse content_type
        c_type: Optional[ContentType] = None
        if isinstance(content_type, ContentType):
            c_type = content_type
        elif isinstance(content_type, str):
            c_type = ContentType.from_str(content_type)

        gt = GripType.from_str(grip_type) if isinstance(grip_type, str) else grip_type
        asq = AnamorphicSqueeze.from_str(anamorphic_squeeze) if isinstance(anamorphic_squeeze, str) else anamorphic_squeeze
        if anamorphic and not asq:
            asq = AnamorphicSqueeze.SQUEEZE_2_0X
        sf = StreakFlare.from_str(streak_flare) if isinstance(streak_flare, str) else streak_flare
        ib = IrisBladeCount.from_str(iris_blades) if isinstance(iris_blades, str) else iris_blades
        gb = GoboPattern.from_str(gobo) if isinstance(gobo, str) else gobo
        gm = GripModifier.from_str(grip_modifier) if isinstance(grip_modifier, str) else grip_modifier
        lr = LightingRatio.from_str(lighting_ratio) if isinstance(lighting_ratio, str) else lighting_ratio
        cs = CopySpace.from_str(copy_space) if isinstance(copy_space, str) else copy_space
        asz = AdSafeZone.from_str(ad_safe_zone) if isinstance(ad_safe_zone, str) else ad_safe_zone

        # 2. Build SceneInput
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
                lighting_preset=lighting_preset,
                capture_mode=capture_mode,
                sharpness_protocol=sharpness_protocol,
                output_resolution=output_resolution,
                suppress_text_branding=suppress_text_branding,
                human_skin_realism=human_skin_realism,
                content_type=c_type,
                text_preservation=text_preservation,
                camera_angle=camera_angle,
                color_mode=color_mode,
                crowd_action=crowd_action,
                product_crop=product_crop,
                sku_color=sku_color,
                cap_geometry=cap_geometry,
                label_kerning=label_kerning,
                material_finish=material_finish,
                seam_geometry=seam_geometry,
                approval_gate_100pct=approval_gate_100pct,
                hand_lock=hand_lock,
                grip_type=gt,
                hand_details=hand_details,
                anamorphic_squeeze=asq,
                streak_flare=sf,
                iris_blades=ib,
                gobo=gb,
                grip_modifier=gm,
                lighting_ratio=lr,
                copy_space=cs,
                ad_safe_zone=asz,
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
            if lighting_preset:
                scene_input.lighting_preset = lighting_preset
            if capture_mode:
                scene_input.capture_mode = capture_mode
            scene_input.sharpness_protocol = sharpness_protocol
            if output_resolution:
                scene_input.output_resolution = output_resolution
            scene_input.suppress_text_branding = suppress_text_branding
            scene_input.human_skin_realism = human_skin_realism
            if c_type:
                scene_input.content_type = c_type
            scene_input.text_preservation = text_preservation
            if camera_angle:
                scene_input.camera_angle = camera_angle
            if color_mode:
                scene_input.color_mode = color_mode
            if crowd_action:
                scene_input.crowd_action = crowd_action
            if product_crop:
                scene_input.product_crop = product_crop
            if sku_color:
                scene_input.sku_color = sku_color
            if cap_geometry:
                scene_input.cap_geometry = cap_geometry
            if label_kerning:
                scene_input.label_kerning = label_kerning
            if material_finish:
                scene_input.material_finish = material_finish
            if seam_geometry:
                scene_input.seam_geometry = seam_geometry
            scene_input.approval_gate_100pct = approval_gate_100pct
            if hand_lock:
                scene_input.hand_lock = hand_lock
            if gt:
                scene_input.grip_type = gt
            if hand_details:
                scene_input.hand_details = hand_details
            if asq:
                scene_input.anamorphic_squeeze = asq
            if sf:
                scene_input.streak_flare = sf
            if ib:
                scene_input.iris_blades = ib
            if gb:
                scene_input.gobo = gb
            if gm:
                scene_input.grip_modifier = gm
            if lr:
                scene_input.lighting_ratio = lr
            if cs:
                scene_input.copy_space = cs
            if asz:
                scene_input.ad_safe_zone = asz

        # 3. Parse target engine
        engine = (
            target
            if isinstance(target, TargetEngine)
            else TargetEngine.from_str(target)
        )

        # 4. Resolve base profile (dynamic auto router, fixed profile, or locked GFX100RF)
        if scene_input.reference and scene_input.reference.mode == ReferenceMode.DEPIXELATE_GFX100RF:
            base = load_profile("fujifilm_gfx100rf")
        elif self.is_auto:
            target_profile_id = auto_select_profile(scene_input)
            base = load_profile(target_profile_id)
        else:
            base = self.base_profile

        # 5. Apply overrides to active profile
        active_profile = apply_overrides(base, scene_input)

        # 6. Compile via target adapter
        adapter = get_adapter(engine)
        payload = adapter.compile(scene_input, active_profile)
        payload.metadata.setdefault("hardware_profile", active_profile.profile_id)
        return payload

    def compile_all(
        self,
        scene: Union[str, SceneInput],
        **kwargs: Any,
    ) -> dict[str, CompiledPayload]:
        """Compile the scene across all registered generation targets at once."""
        results = {}
        for engine in [
            TargetEngine.GPT_IMAGES,
            TargetEngine.IMAGEN,
            TargetEngine.MIDJOURNEY,
            TargetEngine.FLUX,
            TargetEngine.SDXL,
            TargetEngine.RAW,
            TargetEngine.JSON_PROMPT,
        ]:
            results[engine.value] = self.compile(scene, target=engine, **kwargs)
        return results


def compile_scene(
    scene: Union[str, SceneInput],
    profile_name_or_path: str = "phase_one_iq4",
    target_model: Union[str, TargetEngine] = TargetEngine.GPT_IMAGES,
    **kwargs: Any,
) -> CompiledPayload:
    """Convenience helper to initialize compiler and compile a scene in one call."""
    compiler = OpticalCompiler(profile_name_or_path)
    return compiler.compile(scene, target=target_model, **kwargs)


def compile_ab_harness(
    scene: Union[str, SceneInput],
    module_a: str = "sony_a1_ii",
    module_b: str = "phase_one_iq4",
    target: Union[str, TargetEngine] = TargetEngine.GPT_IMAGES,
    **kwargs: Any,
) -> dict[str, Any]:
    """Compile a side-by-side A/B comparison harness swapping only the camera hardware module."""
    compiler_a = OpticalCompiler(module_a)
    compiler_b = OpticalCompiler(module_b)
    res_a = compiler_a.compile(scene, target=target, **kwargs)
    res_b = compiler_b.compile(scene, target=target, **kwargs)
    return {
        "module_a": res_a,
        "module_b": res_b,
        "camera_a": compiler_a.base_profile.title,
        "camera_b": compiler_b.base_profile.title,
    }
