# Standard XL Wildcard Reference

This document provides an overview of the main wildcard files in the `std/xl` namespace, designed for use with the Dynamic Prompts system for AI image generation.

## Core Wildcard Files

### Camera (`__std/xl/camera__`)
Controls camera positioning, angles, distances, and compositional framing. Provides modular combinations of shot types (close-up, wide shot), camera angles (low-angle, high-angle), and viewing perspectives to create professional photographic compositions.

### Character (`__std/xl/character__`)
Defines character poses, body positions, gestures, and expressions. Combines body stances (standing, sitting, kneeling) with arm gestures, head directions, and facial expressions to create natural and dynamic character positioning.

### Details (`__std/xl/details__`)
Adds rich environmental and decorative elements including mystical effects, symbols, creatures, and props. Focuses on tangible details that enhance scenes with accessories, geometric patterns, paint effects, and mechanical elements.

### Distance (`__std/xl/distance__`)
Provides background depth and far-off elements like distant objects, horizon details, and atmospheric background elements. Creates spatial depth without defining complete scenes, adding shadowy figures, distant lights, and weathered structures.

### Environment (`__std/xl/environment__`)
Defines atmospheric conditions and environmental modifiers that enhance base locations with mood and feeling. Includes weather elements, atmospheric effects, lighting atmosphere, and abstract spatial elements like void spaces and swirling motion.

### Lighting (`__std/xl/lighting__`)
Controls illumination quality, placement, mood, and atmospheric lighting effects. Combines light sources (natural, artificial) with placement descriptions (overhead, side lighting) and mood descriptors to create dramatic or subtle lighting scenarios.

### Location (`__std/xl/location__`)
Establishes base physical locations and settings including ancient ruins, industrial spaces, natural environments, and cosmic locations. Provides the foundational "where" of scenes with clean separation from atmospheric modifiers.

### Outfit (`__std/xl/outfit__`)
Describes clothing and fashion elements including garment types, style modifiers, materials, and accessories. Combines base clothing items (dress, coat, bodysuit) with decorative elements, material finishes, and complementary accessories.

### Style (`__std/xl/style__`)
Defines artistic rendering styles and visual approaches including anime, graphic novel, painting mediums, and digital art styles. Controls the overall aesthetic presentation from photorealistic to stylized artistic interpretations.

## Usage Examples

### Individual References
```
# Basic file reference
__std/xl/camera__          # Uses the 'all' category from camera.yaml

# Specific category reference  
__std/xl/camera/angle__    # Uses only the angle subcategory

# Combined references in templates
"__std/xl/character__ with __std/xl/lighting__, __std/xl/style__"
```

### Master Prompt Template
Here's how these wildcards compose together in a complete prompt:

```
masterpiece, best quality,
__std/xl/lumi/all__,
__std/xl/style/all__,
__std/xl/camera/all__,
1girl with {cat|bunny} ears, curvy, {flat|small|medium|large|very large} breasts, bored face, black_sclera,
__std/xl/character/all__, 
wearing __std/xl/outfit/all__
__std/xl/location/all__,
__std/xl/environment/all__, 
__std/xl/distance/all__,
__std/xl/lighting/all__, 
__std/xl/details/all__
```

This creates a complete scene description where each wildcard contributes its specialized domain knowledge while maintaining coherent composition through the template patterns within each file.

## File Relationships

- **camera** + **lighting**: Complete photographic setup
- **character** + **outfit**: Full character description  
- **location** + **environment**: Complete scene setting
- **details** + **distance**: Enhanced scene depth and complexity
- **style**: Applies to all other elements as overarching artistic direction

Each file is designed for modularity, allowing individual categories to be referenced independently while the `all` category provides pre-composed templates for complete descriptions within that domain.