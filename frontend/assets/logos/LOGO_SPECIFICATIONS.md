# Logo Specifications

## Required Logo Files

### Groww Logo
- **File Name**: `groww_logo.png` (preferred) or `groww_logo.svg`
- **Location**: `frontend/assets/logos/`
- **Recommended Dimensions**: 
  - PNG: 120x120px minimum (square format preferred)
  - SVG: Scalable, but should render well at 120x120px
- **Format**: PNG (preferred for better compatibility) or SVG
- **Background**: Transparent background recommended
- **File Size**: Keep under 500KB for optimal loading

### How to Add Logo

1. **For PNG format**:
   - Save your logo as `groww_logo.png`
   - Place it in `frontend/assets/logos/` directory
   - Ensure it has a transparent background
   - Recommended size: 120x120px or larger (will be scaled to 120px width)

2. **For SVG format**:
   - Save your logo as `groww_logo.svg`
   - Place it in `frontend/assets/logos/` directory
   - Ensure it's optimized and has proper viewBox settings

### Fallback Behavior

If the logo file is not found:
- The system will use a styled text placeholder with "Groww" text
- The placeholder uses the brand color gradient

### Current Implementation

The welcome component checks for logos in this order:
1. `frontend/assets/logos/groww_logo.png` (PNG format - preferred)
2. `frontend/assets/logos/groww_logo.svg` (SVG format - fallback)
3. Styled text placeholder (if neither file exists)

### Notes

- Logo will be displayed at 120px width (height will scale proportionally)
- Ensure logo is high quality and readable at the display size
- For best results, use PNG format with transparent background
- Logo should represent the Groww brand identity

