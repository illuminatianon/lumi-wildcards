# Z Image Base Practical Prompting & Sampling Report (ComfyUI)

**Scope:** Prompting methodology + KSampler settings + latent sizing strategy + AuraFlow shifting — written for direct ComfyUI use _and_ easy distillation into reusable LLM prompt templates.

---

## 1) Executive Quickstart (1–2 pages)

### 1.0 Assumptions (so you can sanity-check fast)

- **“Z Image Base” = Tongyi-MAI “Z-Image” (undistilled)** (supports CFG + negative prompts). (Confidence: **High**) ([Hugging Face][1])
- **ComfyUI workflow uses**:
  - **ModelSamplingAuraFlow** node with **shift ≈ 3.0** (often shown as `3`). (Confidence: **High**) ([GitHub][2])
  - **Sampler:** `res_multistep` + **Scheduler:** `simple` as a strong default in official/community workflows. (Confidence: **High**) ([GitHub][2])

- **Recommended parameter envelope (official):**
  - **Resolution:** ~512×512 to 2048×2048 _by total pixel area; any aspect ratio_
  - **Steps:** 28–50
  - **Guidance (CFG):** 3.0–5.0
    (Confidence: **High**) ([Hugging Face][1])

**If any of the above doesn’t match your setup** (e.g., your workflow doesn’t have ModelSamplingAuraFlow), treat this as a mismatch risk and run the “verification experiments” in sections 5 + 6.

---

### 1.1 If you only read one section: do this

#### “One-line” baseline recipe (text-to-image)

- **Size:** start at **1024×1024** (or **1536×864** for 16:9) (Confidence: **High**) ([Hugging Face][1])
- **Sampler / Scheduler:** `res_multistep` + `simple` (Confidence: **High**) ([GitHub][2])
- **Steps:** **36** (within 28–50) (Confidence: **High**) ([Hugging Face][1])
- **CFG:** **4.0** (within 3–5) (Confidence: **High**) ([Hugging Face][1])
- **Denoise:** **1.0** (for pure text-to-image) (Confidence: **High**)
- **AuraFlow shift:** **3.0** (Confidence: **High**) ([DeepWiki][3])
- **Prompt style:** **long, descriptive “brief”** (the model is built for strong prompt adherence and robust negative prompting). (Confidence: **High**) ([Hugging Face][1])

#### Prompt structure (copy this mental order)

**Subject → Composition → Style capsule → Lighting → Camera → Materials → Environment → Post** (Confidence: **High**)

---

### 1.2 Ready-to-run presets (prompt + negative + settings + size + AuraFlow shift)

> These are designed to be pasted into an LLM template system _or_ copied into your ComfyUI notes.
> Each preset assumes **Z Image Base** (CFG+negatives enabled). (Confidence: **High**) ([Hugging Face][1])

---

#### Preset A — Balanced photoreal (16:9 “daily driver”)

(Confidence: **High**)

```yaml
name: ZImageBase_Balanced_Photoreal_16x9
size: { width: 1536, height: 864 } # 16:9, safe-mid MP
auraFlow_shift: 3.0
ksampler:
  sampler: res_multistep
  scheduler: simple
  steps: 36
  cfg: 4.0
  denoise: 1.0
prompt: |
  A candid street portrait of a woman in her late 20s walking past a small neighborhood café at golden hour.
  Subject centered, waist-up framing, natural expression, gentle eye contact. Slight background blur with visible café signage and warm window light.
  Photorealistic documentary photography, natural skin texture, realistic hair strands, subtle imperfections.
  Warm directional sunlight, soft shadows, bounce light from storefront windows.
  50mm lens look, medium depth of field, clean focus on the eyes.
  Cotton jacket fabric texture, metal jewelry with realistic reflections.
  Urban sidewalk scene, people softly out of focus in the background, natural color grading, mild film grain.
negative: |
  watermark, logo, signature, lowres, blurry, out of focus, jpeg artifacts, oversharpened, plastic skin,
  deformed face, asymmetrical eyes, extra fingers, fused fingers, missing fingers, duplicate person
```

Settings basis aligns with official recommended ranges + common ComfyUI workflow defaults. ([Hugging Face][1])

---

#### Preset B — Max quality portrait (4:5 editorial)

(Confidence: **High**)

```yaml
name: ZImageBase_MaxQuality_Portrait_4x5
size: { width: 1024, height: 1280 }
auraFlow_shift: 3.2
ksampler:
  sampler: res_multistep
  scheduler: simple
  steps: 50
  cfg: 4.0
  denoise: 1.0
prompt: |
  High-end editorial portrait of a man in his 30s in a minimalist studio, calm confident expression.
  Tight head-and-shoulders framing, centered, clean background with subtle gradient.
  Luxury fashion photography, realistic skin pores, believable micro-contrast, clean color separation.
  Softbox key light at 45 degrees, gentle rim light, soft shadow falloff.
  85mm lens look, shallow depth of field, tack sharp eyes, smooth bokeh.
  Wool suit fabric weave visible, natural hair detail, accurate catchlights.
  Subtle filmic color grade, no harsh sharpening, professional retouching but still realistic texture.
negative: |
  lowres, blurry, motion blur, overprocessed, plastic skin, waxy skin, acne blobs, pores smeared,
  deformed face, extra limbs, extra fingers, fused fingers, asymmetry, duplicate head, double face,
  watermark, logo, text artifacts
```

Steps/CFG are directly within official guidance; shift is a controlled “detail bias” (see section 6). ([Hugging Face][1])

---

#### Preset C — Cinematic wide (high-MP 16:9 scene)

(Confidence: **Medium** on the exact size choice; **High** on the general approach)

```yaml
name: ZImageBase_CinematicWide_HighMP
size: { width: 2048, height: 1152 } # 16:9, higher MP but still within recommended pixel-area envelope
auraFlow_shift: 3.0
ksampler:
  sampler: res_multistep
  scheduler: simple
  steps: 45
  cfg: 3.5
  denoise: 1.0
prompt: |
  A cinematic establishing shot of a rain-soaked downtown street at night, neon reflections on wet asphalt.
  Wide composition with strong leading lines, subject: a lone person holding an umbrella walking toward camera, lower third of frame.
  Neo-noir film still, realistic atmosphere, volumetric mist, crisp highlights, controlled contrast.
  Mixed lighting: neon signage, street lamps, and storefront spill light, realistic reflections and wet surfaces.
  24mm lens look, deep perspective, slight anamorphic feel, subtle lens flare, sharp environment detail.
  Materials: wet concrete, reflective glass, metal railings, fabric umbrella texture.
  Background: taxis and pedestrians softly blurred, realistic depth cues, film grain, cinematic color grading.
negative: |
  lowres, blurry, washed out, flat lighting, banding, posterization, overexposed highlights,
  duplicate person, extra limbs, weird anatomy, floating objects, watermark, logo
```

Why CFG 3.5 here: high-res scenes often get “over-insistent” with higher guidance; lowering CFG can reduce duplication/composition collapse. (Confidence: **Medium**)
Resolution guidance is from official recs; 2048×1152 fits the “up to 2048×2048 total pixel area” framing. ([Hugging Face][1])

---

#### Preset D — Stylized illustration (clean, graphic)

(Confidence: **Medium** because stylized behavior depends on prompt/style capsule)

```yaml
name: ZImageBase_Stylized_Illustration_Clean
size: { width: 1024, height: 1024 }
auraFlow_shift: 2.8
ksampler:
  sampler: res_multistep
  scheduler: simple
  steps: 34
  cfg: 4.5
  denoise: 1.0
prompt: |
  A stylized illustrated poster of a mountain landscape with a winding river and a small cabin.
  Strong graphic shapes, clean edges, intentional simplified shading, bold readable silhouettes.
  Contemporary illustration style, soft gradient sky, limited color palette, crisp linework, minimal texture.
  Warm sunrise lighting with long shadows, atmospheric depth.
  Wide framing, horizon in upper third, balanced composition, no clutter.
  Matte paper print look, subtle halftone texture, poster design aesthetic.
negative: |
  photorealistic, camera photo, messy detail, noisy texture, muddy colors,
  blurry, lowres, jpeg artifacts, watermark, signature, random text
```

This uses “anti-photoreal” negatives to steer style; keep them **specific**, not a giant “ban list” (see section 3). (Confidence: **Medium**)

---

#### Preset E — Text fidelity (sign/label you can actually read)

(Confidence: **Medium** — text is doable, but still benefits from iteration + sometimes inpaint)

```yaml
name: ZImageBase_TextFidelity_Signage
size: { width: 1344, height: 768 } # 16:9-ish, moderate MP
auraFlow_shift: 3.5
ksampler:
  sampler: res_multistep
  scheduler: simple
  steps: 50
  cfg: 4.5
  denoise: 1.0
prompt: |
  A clean studio product shot of a white cardboard sign on a simple stand.
  The sign contains bold, perfectly legible sans-serif text that reads exactly:
  "OPEN DAILY 8AM–6PM"
  Centered composition, straight-on camera, high contrast black text on white background,
  no distortion, no decorative font, no extra symbols.
  Soft even studio lighting, minimal shadows, crisp focus across the sign.
negative: |
  illegible text, misspelled text, gibberish letters, extra words, distorted typography,
  lowres, blurry, watermark, logo, jpeg artifacts, shadow covering text
```

Z-Image is explicitly positioned as strong in prompt adherence and bilingual text rendering in project materials; still, text benefits from tight constraints + multiple seeds. ([Hugging Face][1])

---

### 1.3 Common failure → fix (mini-table)

| Failure                            | Most likely cause                                               | Fastest fix                                                                                                                             |
| ---------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **“Waxy / plastic skin”**          | CFG too high or prompt asks for “8K ultra smooth” type phrasing | Drop CFG by 0.5; add “natural skin texture, subtle imperfections”; reduce sharpening language (Confidence: **Medium**)                  |
| **Duplicate heads / extra people** | Ambiguous subject count + high-res canvas + high CFG            | Add explicit count (“one person”); lower CFG; reduce size; add compositional anchor (“centered, single subject”) (Confidence: **High**) |
| **Mushy detail**                   | Too few steps or shift too low                                  | Increase steps toward 45–50; increase shift to ~3.2–3.6 (Confidence: **Medium**)                                                        |
| **Composition drift at high MP**   | Pushing resolution without anchoring composition                | Use lower CFG, specify framing, or do 2-pass (native → latent upscale with low denoise) (Confidence: **Medium**)                        |
| **Text gibberish**                 | Text too long / too stylized / low contrast                     | Shorten text; demand sans-serif, high contrast, straight-on; increase steps; consider inpaint pass (Confidence: **Medium**)             |
| **Harsh banding / posterization**  | Over-contrast prompts + aggressive post language                | Add “smooth gradients, no banding”; reduce contrast terms; try different scheduler (Confidence: **Low–Medium**)                         |

---

## 2) Prompting methodology for Z Image Base

Z Image Base is designed for **strong prompt adherence** and **powerful negative prompting** (compared to its Turbo sibling, which disables CFG/negatives). (Confidence: **High**) ([Hugging Face][1])

### 2.1 Prompt structure

#### Recommended ordering (use this every time)

(Confidence: **High**)

1. **Subject** (count, identity, key attributes)
2. **Composition** (framing, camera angle, subject placement, background intent)
3. **Style capsule** (genre + medium + palette + references _in generic terms_)
4. **Lighting** (key light type + direction + mood)
5. **Camera** (lens look, DOF, shot type)
6. **Materials** (fabric, metal, skin, glass, etc.)
7. **Environment** (scene context, era, weather, props)
8. **Post / render constraints** (grain, grade, sharpness, realism)

**Practical reason:** This ordering keeps “must-have scene constraints” early and clusters “look” descriptors later so you can swap style capsules without rewriting the subject. (Confidence: **High**)

#### Literal vs evocative

- Be **literal** for:
  - **Counts** (“one person”, “two hands visible”, “single logo”) (Confidence: **High**)
  - **Text** (exact string, font, placement) (Confidence: **High**)
  - **Composition constraints** (“centered”, “rule of thirds”, “head-and-shoulders”) (Confidence: **High**)

- Be **evocative** for:
  - Mood and vibe (“melancholic”, “serene”, “tense”) (Confidence: **High**)
  - Lighting adjectives (“crepuscular”, “moody rim light”) (Confidence: **Medium**) — because these can be interpreted differently per seed.

#### Token economy (what to cut first vs keep)

Z-Image works well with **long descriptive prompts** (the official examples are paragraph-style). (Confidence: **High**) ([Hugging Face][1])

**Cut first (lowest value per token):** (Confidence: **High**)

- Repeated synonyms (“beautiful, gorgeous, stunning…”)
- Vague quality spam (“masterpiece, best quality, ultra high definition…”)
- Overlapping style references (“cinematic film still” + “DSLR photo” + “anime”)
- Conflicting instructions (“shallow DOF” + “everything in focus”)

**Keep (highest value per token):** (Confidence: **High**)

- Subject nouns + counts
- Framing and camera distance
- Lighting type and direction
- Material cues (they reduce “AI plastic”)
- Environment anchors (time, place, weather)

#### Weighting/emphasis guidance (if supported)

**Assumption:** Your ComfyUI text encode node supports standard prompt emphasis syntax like `(term:1.2)` (common in many ComfyUI encoders). (Confidence: **Medium**)
**Safest default:** Don’t rely on weighting for Z Image Base; use plain language emphasis (“the main subject is…”, “centered”). (Confidence: **High**)

**Quick verification experiment (2 minutes):**

1. Prompt: `a red cube next to a blue cube, simple studio scene`
2. Variant A: `(red cube:1.6), blue cube`
3. Variant B: `red cube, (blue cube:1.6)`
   If weighting works, the emphasized cube becomes more dominant _without_ you rewriting the prompt. (Confidence: **High**)

**If weighting works, use it like this:**

```text
(one person:1.3), centered composition, (clean legible text:1.25), realistic skin texture
```

---

### 2.2 Style strategies

#### Locking a consistent style across generations

**Goal:** Change _content_ while holding _look_ stable. (Confidence: **High**)

Use a **style capsule** that contains:

- medium/genre (editorial photo, anime cel, watercolor)
- lighting signature (softbox + rim, neon noir, overcast diffused)
- camera signature (50mm, 85mm shallow DOF, etc.)
- grading signature (Kodak-like, cool teal/orange, matte print)
- texture signature (film grain, paper tooth, halftone)

Keep that capsule **verbatim** across runs. (Confidence: **High**)

#### Vary content while holding style constant

- Keep style capsule fixed
- Swap only:
  - subject nouns
  - environment nouns
  - props
  - action verbs

- Leave camera/lighting/materials intact. (Confidence: **High**)

#### Strategies by target

**Photoreal** (Confidence: **High**)

- Use: “natural skin texture”, “realistic reflections”, “subsurface scattering”, “micro-contrast”
- Avoid: “perfect flawless skin”, “ultra smooth”, “CGI render” (unless you want that)

**Illustration/anime/stylized** (Confidence: **Medium**)

- Be explicit: “flat shading / cel shading”, “clean linework”, “limited palette”, “poster design”
- Use negative prompt to ban “photo” and “realistic skin pores” if it keeps drifting.

**Cinematic** (Confidence: **High**)

- Anchor lens + lighting: “24mm wide establishing shot”, “anamorphic flare”, “volumetric haze”
- Use environment anchors: time of day, weather, practical lights.

**Product / portrait / landscape** (Confidence: **High**)

- Product: “seamless backdrop”, “soft even studio light”, “no clutter”, “sharp edges”
- Portrait: “85mm”, “catchlights”, “skin texture”, “clean background separation”
- Landscape: “atmospheric perspective”, “foreground midground background”, “leading lines”

#### Style capsules you can append downstream (copy-ready)

**Capsule 1: Editorial photoreal**

```text
Luxury editorial photography, realistic skin texture, natural imperfections, clean color separation, subtle film grain, professional retouching without plastic skin
```

**Capsule 2: Cinematic neo-noir**

```text
Neo-noir cinematic film still, moody contrast, volumetric haze, practical lights, subtle anamorphic lens flare, film grain, cinematic color grading
```

**Capsule 3: Clean illustrated poster**

```text
Contemporary illustration poster, clean linework, flat or cel shading, limited color palette, crisp silhouettes, matte paper print texture
```

(Confidence: **High** that capsules-as-blocks are effective; the exact phrasing can be tuned.)

---

### 2.3 Composition control

#### Framing + focal length language (practical mapping)

(Confidence: **High**)

- **14–24mm:** ultra-wide / establishing / dramatic perspective
- **35mm:** environmental portrait / natural perspective
- **50mm:** “default human-ish” perspective, good general purpose
- **85–135mm:** portraits, flattering compression, strong background separation
- **Macro:** product detail, textures

**Concrete example (composition-first prompt line):**

```text
Subject centered, head-and-shoulders portrait, 85mm lens look, shallow depth of field, clean studio background
```

#### Centering vs off-center subjects

**Centering (for clarity / product / text):** (Confidence: **High**)

- “centered composition, symmetrical framing, equal negative space”

**Off-center (for cinematic / dynamic):** (Confidence: **High**)

- “subject on left third, negative space on right, background storytelling element in empty space”

#### Prevent “dead space” or “punting” one side

Common cause: you ask for wide canvas but don’t specify what fills the sides. (Confidence: **High**)
Fix: explicitly allocate background detail. (Confidence: **High**)

**Example fix prompt fragment:**

```text
Wide 16:9 frame; subject in lower-left third; right side contains neon signs and storefront windows with reflections; no empty blank wall
```

#### Regional prompting / masking / control mechanisms (how they interact with prompts)

If you need **layout guarantees**, prompts alone will sometimes drift—especially at high MP. (Confidence: **Medium**)

**ComfyUI-friendly approach:**

- Keep the **global prompt** describing the overall scene + style capsule.
- Use **regional conditioning (areas/masks)** for “local must-haves”:
  - left region: subject A
  - right region: subject B
  - center region: text/sign/product label

**Concrete example (regional prompt text you’d feed into separate conditioning nodes):**

```text
LEFT REGION: a single woman holding an umbrella, walking toward camera, sharp focus, detailed face
RIGHT REGION: neon storefront windows and reflections, no people, environmental detail only
GLOBAL: neo-noir cinematic film still, volumetric mist, rain reflections, 24mm lens look
```

(Confidence: **Medium**) — exact node names vary, but the concept is stable.

---

### 2.4 Text and symbols (if applicable)

Z-Image family is marketed as strong at **bilingual text rendering**, and Z-Image Base supports CFG/negatives for tighter control. (Confidence: **High**) ([GitHub][4])

#### What tends to work

(Confidence: **Medium–High**)

- Short text (1–6 words)
- High contrast background
- Straight-on camera, minimal perspective distortion
- Sans-serif font requests
- Text on a flat sign/label/board

#### What tends to fail

(Confidence: **High**)

- Long paragraphs
- Curved / circular text
- Small type on busy textures
- Decorative fonts + strong perspective

#### Best practices for legible text

(Confidence: **High**)

- Put the exact text in quotes on its own line.
- Specify: **font style**, **placement**, **no extra words**, **no distortion**.
- Increase steps toward **45–50** for text-critical images.
- Consider slightly higher shift (e.g., **3.3–3.7**) if text remains mushy. (Confidence: **Medium**)

**Concrete example prompt fragment:**

```text
Clean, perfectly legible sans-serif text reading exactly: "NO PARKING"
Centered, high contrast black text on white sign, straight-on camera, no distortion, no extra symbols
```

---

## 3) Negative prompts (and when NOT to use them)

Z-Image Base supports **negative prompting** and responds with high fidelity to it. (Confidence: **High**) ([Hugging Face][1])

### 3.1 Default negative prompt (balanced)

(Confidence: **High**)

```text
watermark, logo, signature,
lowres, blurry, out of focus, jpeg artifacts,
deformed face, asymmetrical eyes, bad anatomy,
extra fingers, fused fingers, missing fingers,
duplicate person, extra limbs,
oversharpened, plastic skin
```

### 3.2 Variants by goal

#### Photoreal cleanliness (skin + optics)

(Confidence: **High**)

```text
plastic skin, waxy skin, overprocessed, over-smoothed,
oversharpened, HDR look, crunchy texture,
blurry, lowres, jpeg artifacts, watermark, logo, signature,
deformed face, asymmetry, extra fingers, fused fingers, duplicate person
```

#### Stylized cleanliness (keep it graphic)

(Confidence: **Medium**)

```text
photorealistic, camera photo, realistic skin pores,
messy detail, noisy texture, muddy colors,
blurry, lowres, jpeg artifacts, watermark, signature, random text
```

#### Avoiding artifacts (hands/faces/duplicates/asymmetry)

(Confidence: **High**)

```text
deformed hands, bad hands, extra fingers, fused fingers, missing fingers,
deformed face, double face, asymmetrical eyes, crooked teeth,
duplicate person, duplicate head, extra limbs
```

#### Prevent blur / low-detail / compression look

(Confidence: **High**)

```text
blurry, out of focus, low detail, smeared textures,
jpeg artifacts, compression artifacts, banding, posterization
```

### 3.3 When NOT to use negatives (or use minimal negatives)

**Minimal negative philosophy (recommended default)**
Use negatives only for **specific recurring failures** you actually see. (Confidence: **High**)
Reason: Overly broad negatives can suppress legitimate detail or introduce “sterile” images. (Confidence: **High**)

**Heavy negative philosophy (only when you must)**
Use a heavy negative when:

- you’re generating large batches
- you need consistent cleanliness across seeds
- you’re fighting a persistent artifact (hands, watermark, duplicates)
  (Confidence: **Medium**)

**Failure modes from overly broad negatives** (what it looks like)

- “Lifeless” images (you accidentally negated mood/lighting cues) (Confidence: **Medium**)
- Washed textures (negatives like “noise, grain, texture” can remove desirable micro-detail) (Confidence: **Medium**)
- Prompt conflict (neg “text” while asking for a sign) (Confidence: **High**)

**Concrete example of a “minimal negative” setup:**

```text
watermark, logo, signature, duplicate person, extra fingers
```

---

## 4) KSampler settings deep dive

### 4.1 Core concepts in plain language

#### Steps vs quality vs artifact risk

- **More steps (28 → 50)** generally improve refinement and reduce mushiness, with diminishing returns near the top end. (Confidence: **High**) ([Hugging Face][1])
- Too many steps _can_ push toward over-refinement / “crunch” depending on prompt + shift. (Confidence: **Medium**)

**Practical take:** Start at **36**, go to **50** for text/detail-critical work. (Confidence: **High**) ([Hugging Face][1])

#### CFG behavior: low vs high

Official recommended **CFG 3–5** is a strong indicator that Z-Image Base prefers _moderate_ guidance. (Confidence: **High**) ([Hugging Face][1])

- **Low CFG (~3.0–3.5):** more natural variation, sometimes looser adherence (Confidence: **High**)
- **Mid CFG (~4.0):** best balance for most prompts (Confidence: **High**)
- **High CFG (~4.8–5.5):** stronger adherence but higher risk of “overbaked” textures, weird anatomy emphasis, duplication in complex scenes (Confidence: **Medium**)

#### Sampler vs scheduler roles (decision-focused)

- **Sampler:** the numerical method that decides _how_ each denoise step updates the latent (detail feel, stability). (Confidence: **High**)
- **Scheduler:** the “timestep/sigma schedule” controlling _where_ those steps land along noise→clean trajectory (affects texture, contrast, composition stability). (Confidence: **High**)

---

### 4.2 Recommended setting ranges (table)

> **Primary default** for Z Image Base in ComfyUI: `res_multistep` + `simple` + shift 3.0. (Confidence: **High**) ([GitHub][2])

| Goal                      | Sampler       | Scheduler | Steps (range → typical) | CFG (range → typical) | Denoise | Notes / pitfalls                                                                                                                              |
| ------------------------- | ------------- | --------: | ----------------------: | --------------------: | ------: | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Speed draft**           | res_multistep |    simple |       28–34 → **28–30** |     3.0–4.5 → **4.0** |     1.0 | Lower res instead of starving steps. (Confidence: **High**) ([Hugging Face][1])                                                               |
| **Balanced**              | res_multistep |    simple |          32–40 → **36** |     3.5–4.5 → **4.0** |     1.0 | The “daily driver” zone. (Confidence: **High**) ([Hugging Face][1])                                                                           |
| **Max quality**           | res_multistep |    simple |          45–50 → **50** |     3.5–4.5 → **4.0** |     1.0 | Watch oversharpen if prompt asks for “ultra crisp”. (Confidence: **High** on steps range; **Medium** on oversharpen risk) ([Hugging Face][1]) |
| **High detail / texture** | res_multistep |    simple |          40–50 → **45** |     3.5–5.0 → **4.5** |     1.0 | Consider slightly higher shift (3.2–3.6). (Confidence: **Medium**)                                                                            |
| **Stylized**              | res_multistep |    simple |          30–40 → **34** |     3.5–5.0 → **4.5** |     1.0 | Use style capsule + targeted negatives; avoid mixed media conflicts. (Confidence: **Medium**)                                                 |
| **Realism (faces)**       | res_multistep |    simple |       40–50 → **45–50** |     3.0–4.5 → **4.0** |     1.0 | If you have CFG normalization available, enable for realism (see note). (Confidence: **Medium**) ([GitHub][4])                                |
| **Portrait**              | res_multistep |    simple |          35–50 → **45** |     3.5–4.5 → **4.0** |     1.0 | Lens anchoring (85mm) reduces distortion. (Confidence: **High**)                                                                              |
| **Landscape**             | res_multistep |    simple |       32–45 → **36–40** |     3.0–4.0 → **3.5** |     1.0 | Too high CFG can clone elements (trees/buildings). (Confidence: **Medium**)                                                                   |

**CFG normalization note (model-specific):** Z-Image repo suggests `cfg_normalization=False` for “general stylism” and `True` for realism (in diffusers). ComfyUI may not expose this directly; treat it as optional if your workflow has a CFG-normalization/rescale node. (Confidence: **Medium**) ([GitHub][4])

---

### 4.3 Samplers

#### The practical Z-Image Base default

- **res_multistep** is used in common Z-Image ComfyUI workflows. (Confidence: **High**) ([GitHub][2])
- It was introduced to ComfyUI from NVIDIA Cosmos sampling code and is described as usable with supported models. (Confidence: **Medium**) ([mimicpc.com][5])

#### Common samplers you may try (with caveats)

> **Assumption:** Your ComfyUI build offers standard samplers (Euler / DPM++ / UniPC) even for this model. (Confidence: **Medium**)

- **Euler:** fast baseline; sometimes “samey” across seeds. (Confidence: **Low–Medium**)
- **Euler a (ancestral):** can add pleasant variation; sometimes softer/less stable. (Confidence: **Low–Medium**)
- **DPM++ SDE variants:** community testing (not official) reports sharper/cleaner results vs Euler and good diversity, especially paired with Beta/DDIM Uniform schedulers. (Confidence: **Low–Medium**) ([myaiforce.com][6])
- **UniPC:** often stable and detailed on many models; treat as “try if default disappoints.” (Confidence: **Low**)

#### Default pick + second pick list

- **Default pick:** `res_multistep` (Confidence: **High**) ([GitHub][2])
- **Second pick (exploration):** DPM++ SDE (if your workflow supports it cleanly) (Confidence: **Low–Medium**) ([myaiforce.com][6])

**Quick verification experiment (sampler sanity check):**

- Fix: prompt + seed + size + steps (36) + CFG (4) + shift (3)
- Compare: `res_multistep` vs `euler` vs `dpmpp_sde`
  If non-default samplers create “melt/garbage,” revert—your build might not map these samplers well to this model type. (Confidence: **High**)

---

### 4.4 Schedulers

#### Safe default

- **simple** is used in common Z-Image ComfyUI workflows and works reliably. (Confidence: **High**) ([GitHub][2])

#### Other schedulers (optional exploration)

(Confidence: **Low–Medium** overall)

- **Karras:** often emphasizes late-stage refinement; can increase contrast/sharpness.
- **Exponential:** different step spacing; sometimes smoother gradients.
- **Beta / DDIM Uniform:** community tests report these can improve variety/quality for some Z-Image workflows. ([myaiforce.com][6])

**Guideline:** Change scheduler only after you have a stable baseline with `simple`. (Confidence: **High**)

---

### 4.5 Steps & CFG interaction (rules of thumb)

#### Rules you can apply blindly

(Confidence: **High**)

- If you **increase steps**, you can often **decrease CFG slightly** to avoid “overbaked” look.
  - Example: 36 steps @ CFG 4.0 → 50 steps @ CFG 3.5–4.0

- If you **increase CFG**, consider **reducing steps** slightly or **reducing shift** to keep composition stable.
  - Example: CFG 4.8 feels too rigid → drop to 4.0 or shift from 3.5 → 3.0

- If image is **mushy**, raise **steps first**, then raise **shift**, then raise **CFG**. (Confidence: **Medium**)

#### Mini-matrix (fast tuning)

(Confidence: **Medium**)

| Symptom                    |     Steps |       CFG |         Shift |
| -------------------------- | --------: | --------: | ------------: |
| Too loose / ignores prompt |         + | + (small) | 0 / + (small) |
| Too rigid / “overcooked”   |     0 / - |         - |             - |
| Mushy textures             |         + |     0 / + |             + |
| Duplicates / cloning       | + (small) |         - |         0 / - |

---

## 5) Latent size restrictions & resolution strategy

### 5.1 Known constraints (and what’s assumed)

#### Known (official)

- **Resolution target:** **512×512 to 2048×2048** (total pixel area, any aspect ratio). (Confidence: **High**) ([Hugging Face][1])

#### Observed in ComfyUI workflows

- Z-Image workflows commonly initialize latents with **EmptySD3LatentImage** (SD3 latent format). (Confidence: **High**) ([GitHub][2])
- EmptySD3LatentImage produces an SD3 latent tensor with **16 channels** and spatial size roughly **(H/8, W/8)**. (Confidence: **Medium**) ([comfyui.dev][7])

#### Assumption (safe)

- **Width and height should be multiples of 8** (so latent dims are integers and VAE decode is clean). (Confidence: **High**)
  **Verification experiment:** Try a “bad” size like 1025×1025; ComfyUI will either error or internally adjust. If it errors, you’ve confirmed the constraint. (Confidence: **High**)

---

### 5.2 Recommended resolution menu

> Use these as “resolution presets” for repeatable workflows.
> All sizes below are **multiples of 8**. (Confidence: **High**)

#### Safe defaults (start here)

(Confidence: **High**)

- **1:1**: 1024×1024
- **16:9**: 1536×864 (great balance)
- **3:2**: 1536×1024
- **4:5**: 1024×1280 (portrait editorial)
- **2:3**: 1024×1536 (taller portrait)

#### High-MP “push it” sizes (within the 2048×2048 area envelope)

(Confidence: **Medium**)

- **1:1**: 1792×1792 (big but not max)
- **1:1**: 2048×2048 (max-ish) ([Hugging Face][1])
- **16:9**: 2048×1152
- **3:2**: 2048×1360
- **4:5**: 1536×1920

**High-MP best practice:** increase steps (45–50) and keep CFG in the lower-mid range (3.5–4.0) to reduce cloning and composition drift. (Confidence: **Medium**) ([Hugging Face][1])

---

### 5.3 Common high-resolution failure modes + mitigation

#### A) Duplication (extra people, repeated objects)

- **Why it happens:** more canvas invites the model to “fill” space, especially if subject count isn’t constrained. (Confidence: **High**)
- **Fixes (fastest first):**
  1. Add explicit count: “**one** person, **single** subject” (Confidence: **High**)
  2. Lower CFG by 0.5 (Confidence: **Medium**)
  3. Reduce resolution or do a 2-pass upscale workflow (Confidence: **Medium**)

#### B) Edge artifacts / weird borders

- **Fixes:**
  - Avoid max resolution until prompt is stable (Confidence: **High**)
  - Add “clean frame edges, no cut-off limbs, no cropped face” (Confidence: **Medium**)
  - Reduce shift slightly (3.5 → 3.0) if edges become overly “crisp/noisy” (Confidence: **Low–Medium**)

#### C) Composition drift (subject moves, camera changes)

- **Fixes:**
  - Anchor framing early (“centered, waist-up, eye-level”) (Confidence: **High**)
  - Lower CFG slightly (Confidence: **Medium**)
  - Consider doing composition at 1024px, then upscale with low denoise (Confidence: **High**)

---

### 5.4 Upscale vs native resolution decision guide

**Use native high resolution when:** (Confidence: **High**)

- you need _true_ detail everywhere (cityscapes, interiors)
- you’re doing text that must be sharp
- you can afford steps 45–50 at high MP

**Use 2-pass (native → upscale) when:** (Confidence: **High**)

- composition is the priority
- you’re iterating quickly and want stability
- you want to avoid high-res duplication

**Practical 2-pass recipe (example):**

1. Generate at **1536×864**, steps 36, CFG 4, shift 3.0
2. Latent upscale to **2048×1152**
3. Second KSampler pass with **denoise 0.20–0.35**, steps 20–30, CFG 3.5–4.0, shift 3.2
   (Confidence: **Medium** — exact upscale node choices vary)

---

## 6) AuraFlow shifting

### 6.1 Interpretation (what “AuraFlow shifting” means here)

**Interpretation used in this report:**
In ComfyUI, **“AuraFlow shifting” refers to the `shift` parameter in the `ModelSamplingAuraFlow` node** used by flow-matching / rectified-flow style models (including Z-Image workflows). (Confidence: **High**) ([GitHub][2])

### 6.2 What shifting does (practical definition)

Z-Image’s scheduler uses a **shifted sigma schedule** (static shifting by default), transforming sigma like:

`shifted_sigma = shift * sigma / (1 + (shift - 1) * sigma)` (Confidence: **High**) ([DeepWiki][3])

**Practical effect:**

- Higher shift tends to **spend more of your steps in lower-noise refinement**, which can increase perceived detail/texture. (Confidence: **Medium**) ([DeepWiki][3])
- Lower shift tends to **spend relatively more effort earlier**, sometimes improving global structure/variation. (Confidence: **Low–Medium**)

### 6.3 Recommended ranges and presets

#### Safe defaults

- **Shift = 3.0** (matches defaults shown for Z-Image and the scheduler default shift value). (Confidence: **High**) ([DeepWiki][3])

#### Practical tuning range (most users)

(Confidence: **Medium**)

- **2.6–2.9:** more “open” / structural / potentially more varied
- **3.0–3.2:** balanced (recommended)
- **3.3–3.7:** detail bias, can help text and fine texture
- **>3.8:** use cautiously; may over-refine / sharpen artifacts

### 6.4 Troubleshooting shift

#### Too much shifting (symptoms)

(Confidence: **Medium**)

- crunchy micro-texture
- halos / oversharpen feel
- “too tight” adherence, less interesting variation

**Fix:** reduce shift by 0.2–0.5; optionally lower steps or CFG slightly.

#### Too little shifting (symptoms)

(Confidence: **Medium**)

- mushy textures
- weak micro-detail
- text edges look soft

**Fix:** increase shift by 0.2–0.6; increase steps toward 45–50.

### 6.5 Mini experiment plan (fastest way to tune)

(Confidence: **High**)

Use **one prompt**, **one seed**, **one size** (e.g., 1536×864), and hold **steps=36, CFG=4** fixed.

Run:

- shift **2.7**
- shift **3.0**
- shift **3.3**
- shift **3.6**

Pick the best baseline, then only fine-tune by ±0.2.

---

## 7) Troubleshooting & diagnostics

### 7.1 Artifact taxonomy (cause → fix)

> Treat this like a decision tree: **Prompt → CFG → Steps → Shift → Size** (in that order). (Confidence: **High**)

#### Duplicates (extra people / extra heads / cloned objects)

- Likely causes:
  - ambiguous subject count (Confidence: **High**)
  - high resolution without composition anchors (Confidence: **High**)
  - CFG too high for complex scene (Confidence: **Medium**)

- Fixes:
  - prompt: “one person, single subject” + placement (“centered”) (Confidence: **High**)
  - settings: lower CFG 0.5, increase steps a bit, reduce size (Confidence: **Medium**)
  - shift: try slightly lower (3.2 → 3.0 → 2.8) if clones persist (Confidence: **Low–Medium**)

#### Warped faces/hands

- Likely causes:
  - too few steps for portrait detail (Confidence: **High**)
  - too much sharpening language (Confidence: **Medium**)
  - extreme wide lens on close subject (Confidence: **High**)

- Fixes:
  - steps: push to 45–50 (Confidence: **High**) ([Hugging Face][1])
  - prompt: specify “hands not visible” _or_ “hands visible, five fingers each, natural pose” (Confidence: **Medium**)
  - composition: “85mm lens look” for faces (Confidence: **High**)
  - fallback: inpaint hands/face (Confidence: **High**)

#### Mushy detail / “airbrushed”

- Likely causes: steps too low, shift too low, prompt lacks material cues (Confidence: **High**)
- Fixes:
  - add materials: “fabric weave, realistic reflections, skin pores” (Confidence: **High**)
  - steps up (36 → 45–50) (Confidence: **High**) ([Hugging Face][1])
  - shift up (3.0 → 3.3) (Confidence: **Medium**)

#### Over-sharpening / crunchy texture

- Likely causes: shift too high + “ultra sharp” prompt + high steps (Confidence: **Medium**)
- Fixes:
  - prompt: add “natural softness, subtle grain, no harsh sharpening” (Confidence: **High**)
  - shift down (3.6 → 3.2 → 3.0) (Confidence: **Medium**)
  - CFG down slightly (Confidence: **Medium**)

#### “Right-side punt” (subject pushed or empty space on one side)

- Likely causes: wide aspect ratio without explicit placement + background intent (Confidence: **High**)
- Fixes:
  - prompt: “subject centered” or “subject on left third, right side contains…” (Confidence: **High**)
  - reduce resolution while iterating composition (Confidence: **High**)
  - lower CFG if it keeps re-framing (Confidence: **Low–Medium**)

#### Banding / posterization

- Likely causes: aggressive contrast + some scheduler behaviors (Confidence: **Low–Medium**)
- Fixes:
  - prompt: “smooth gradients, no banding, filmic rolloff” (Confidence: **Medium**)
  - try alternate scheduler (beta / karras / exponential) (Confidence: **Low**)
  - add mild grain (Confidence: **Medium**)

#### Noise / grain where you don’t want it

- Likely causes: low steps or prompt calls for “grain/noise” (Confidence: **High**)
- Fixes:
  - raise steps; remove “grain” terms; keep “clean studio lighting” (Confidence: **High**)

#### Flat lighting / dull image

- Likely causes: prompt lacks lighting direction + environment anchors (Confidence: **High**)
- Fix:
  - specify key light direction/type, add rim/bounce, add time-of-day (Confidence: **High**)

### 7.2 Diagnostics workflow (fast)

(Confidence: **High**)

1. **Lock seed**
2. Fix prompt and only change **one knob** at a time:
   - CFG sweep: 3.0 / 4.0 / 5.0
   - Steps sweep: 28 / 36 / 50
   - Shift sweep: 2.8 / 3.0 / 3.4

3. Only after that: change size or scheduler.

---

## 8) Distillation outputs for downstream LLM prompting

### 8.1 Prompt skeleton with slots (copy-ready)

```text
[SUBJECT_COUNT + SUBJECT_IDENTITY + KEY ATTRIBUTES].
[PRIMARY ACTION / POSE]. [KEY PROPS].

COMPOSITION: [FRAMING], [CAMERA ANGLE], [SUBJECT PLACEMENT], [BACKGROUND INTENT].

STYLE: [STYLE CAPSULE].

LIGHTING: [KEY LIGHT TYPE + DIRECTION], [FILL/RIM], [MOOD].

CAMERA: [LENS LOOK], [DEPTH OF FIELD], [FOCUS TARGET].

MATERIALS: [2–5 MATERIAL CUES].

ENVIRONMENT: [LOCATION/ERA/WEATHER], [BACKGROUND DETAILS].

POST: [COLOR GRADE], [GRAIN], [SHARPNESS CONSTRAINTS].
```

**Example filled (short):**

```text
One person: a middle-aged chef in a white jacket, friendly expression.
Standing behind a stainless-steel counter, hands resting naturally.

COMPOSITION: centered, waist-up, eye-level, restaurant kitchen background softly blurred.

STYLE: Luxury editorial photography, realistic skin texture, subtle film grain.

LIGHTING: softbox key light from camera-left, gentle rim light, warm practical lights in background.

CAMERA: 50mm lens look, medium depth of field, sharp focus on the eyes.

MATERIALS: stainless steel, cotton fabric weave, skin pores, glass reflections.

ENVIRONMENT: modern kitchen, warm ambient light, clean but lived-in.

POST: natural color grade, no harsh sharpening.
```

---

### 8.2 Negative prompt skeleton (minimal + heavy)

**Minimal negative (recommended default):**

```text
watermark, logo, signature, lowres, blurry, jpeg artifacts, duplicate person, extra fingers
```

**Heavy negative (only when needed):**

```text
watermark, logo, signature,
lowres, blurry, out of focus, jpeg artifacts, banding, posterization,
deformed face, asymmetry, double face, duplicate head,
bad anatomy, extra limbs, extra fingers, fused fingers, missing fingers,
oversharpened, plastic skin, waxy skin, overprocessed
```

---

### 8.3 Preset blocks (JSON for ComfyUI/KSampler-like use)

```json
[
  {
    "name": "Balanced_Photoreal_16x9",
    "width": 1536,
    "height": 864,
    "shift": 3.0,
    "sampler": "res_multistep",
    "scheduler": "simple",
    "steps": 36,
    "cfg": 4.0,
    "denoise": 1.0,
    "prompt_template": "[SUBJECT]. COMPOSITION: [COMP]. STYLE: [STYLE]. LIGHTING: [LIGHT]. CAMERA: [CAM]. MATERIALS: [MAT]. ENV: [ENV]. POST: [POST].",
    "negative_template": "watermark, logo, signature, lowres, blurry, jpeg artifacts, extra fingers, fused fingers, duplicate person"
  },
  {
    "name": "MaxQuality_Portrait_4x5",
    "width": 1024,
    "height": 1280,
    "shift": 3.2,
    "sampler": "res_multistep",
    "scheduler": "simple",
    "steps": 50,
    "cfg": 4.0,
    "denoise": 1.0,
    "prompt_template": "[SUBJECT]. Tight head-and-shoulders portrait. [STYLE_CAPSULE]. Softbox lighting. 85mm lens look. Natural skin texture.",
    "negative_template": "lowres, blurry, plastic skin, overprocessed, deformed face, extra fingers, fused fingers, double face, watermark"
  },
  {
    "name": "CinematicWide_HighMP",
    "width": 2048,
    "height": 1152,
    "shift": 3.0,
    "sampler": "res_multistep",
    "scheduler": "simple",
    "steps": 45,
    "cfg": 3.5,
    "denoise": 1.0,
    "prompt_template": "Cinematic establishing shot: [SCENE]. Wide 16:9, leading lines, subject in lower third. [STYLE_CAPSULE]. 24mm lens look. Volumetric haze.",
    "negative_template": "lowres, blurry, banding, posterization, duplicate person, extra limbs, watermark, logo"
  },
  {
    "name": "Stylized_Illustration_Clean",
    "width": 1024,
    "height": 1024,
    "shift": 2.8,
    "sampler": "res_multistep",
    "scheduler": "simple",
    "steps": 34,
    "cfg": 4.5,
    "denoise": 1.0,
    "prompt_template": "Illustrated poster: [SUBJECT_SCENE]. Clean linework, cel shading, limited palette, crisp silhouettes, matte print texture.",
    "negative_template": "photorealistic, camera photo, messy detail, muddy colors, blurry, watermark, signature"
  },
  {
    "name": "TextFidelity_Signage",
    "width": 1344,
    "height": 768,
    "shift": 3.5,
    "sampler": "res_multistep",
    "scheduler": "simple",
    "steps": 50,
    "cfg": 4.5,
    "denoise": 1.0,
    "prompt_template": "A clean studio shot of a sign with perfectly legible sans-serif text reading exactly: \"[TEXT]\". Centered, straight-on, high contrast.",
    "negative_template": "illegible text, misspelled text, gibberish letters, extra words, distorted typography, blurry, watermark, logo"
  }
]
```

---

## If you only run three tests to calibrate this model, run these

1. **Baseline sanity** (Confidence: **High**)
   - 1024×1024, res_multistep/simple, steps 36, CFG 4, shift 3
   - One photoreal portrait prompt + minimal negative
   - Goal: confirm your pipeline is “wired correctly” and looks normal.

2. **Shift sweep** (Confidence: **High**)
   - Same seed/prompt/settings, test shift: 2.8 / 3.0 / 3.3 / 3.6
   - Goal: find your preferred detail vs structure balance.

3. **Steps–CFG sweet spot** (Confidence: **High**)
   - Fix shift at your chosen value
   - Test: (steps 28, cfg 4.5) vs (steps 36, cfg 4.0) vs (steps 50, cfg 3.5–4.0)
   - Goal: pick your default preset for your GPU + preferred look.

---

If you want, I can also provide a **single “LLM prompt-to-preset compiler” template** (inputs: subject/style/composition; outputs: JSON preset + final positive/negative strings) — but the blocks above are already structured to do that directly.

[1]: https://huggingface.co/Tongyi-MAI/Z-Image "https://huggingface.co/Tongyi-MAI/Z-Image"
[2]: https://raw.githubusercontent.com/Comfy-Org/workflow_templates/refs/heads/main/templates/image_z_image.json "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/refs/heads/main/templates/image_z_image.json"
[3]: https://deepwiki.com/cosmicoxytocin/Z-Image/3.4-diffusion-scheduler "https://deepwiki.com/cosmicoxytocin/Z-Image/3.4-diffusion-scheduler"
[4]: https://github.com/Tongyi-MAI/Z-Image "https://github.com/Tongyi-MAI/Z-Image"
[5]: https://www.mimicpc.com/learn/how-to-generate-ai-videos-with-nvidia-cosmos-in-comfyui "https://www.mimicpc.com/learn/how-to-generate-ai-videos-with-nvidia-cosmos-in-comfyui"
[6]: https://myaiforce.com/z-image-samplers-schedulers/ "https://myaiforce.com/z-image-samplers-schedulers/"
[7]: https://comfyui.dev/docs/guides/nodes/emptysd3latentimage/ "https://comfyui.dev/docs/guides/nodes/emptysd3latentimage/"
