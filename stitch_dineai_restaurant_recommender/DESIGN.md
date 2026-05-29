---
name: Gourmet Intelligence
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#5b403f'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#5d5c74'
  on-secondary: '#ffffff'
  secondary-container: '#e2e0fc'
  on-secondary-container: '#63627a'
  tertiary: '#705d00'
  on-tertiary: '#ffffff'
  tertiary-container: '#c9a900'
  on-tertiary-container: '#4c3f00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e2e0fc'
  secondary-fixed-dim: '#c6c4df'
  on-secondary-fixed: '#1a1a2e'
  on-secondary-fixed-variant: '#45455b'
  tertiary-fixed: '#ffe16d'
  tertiary-fixed-dim: '#e9c400'
  on-tertiary-fixed: '#221b00'
  on-tertiary-fixed-variant: '#544600'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  headline-display:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 26px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: '1.55'
    letterSpacing: 0px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  price-tag:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-margin-desktop: 120px
  container-margin-mobile: 20px
  gutter: 16px
  section-gap: 40px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style

The design system establishes a high-end, appetizing, and intelligent interface tailored for the Indian culinary landscape. It balances the urgency of hunger with the precision of AI-driven curation. 

The style is **Corporate / Modern** with subtle **Glassmorphism** overlays to signify "smart" layers. It avoids the cluttered density of traditional delivery apps, favoring generous whitespace and high-quality food photography. The emotional response should be one of discovery and reliability—transforming the chore of "deciding what to eat" into a curated, premium experience. AI interactions are never intrusive; they appear as "magical" enhancements to the standard search and discovery flow.

## Colors

The palette leverages the energy of **Primary Red (#E23744)** to stimulate appetite, grounded by a **Dark Charcoal (#1A1A2E)** shell for a premium, night-out aesthetic. 

- **Primary:** Used for call-to-action buttons, active states, and brand marks.
- **Surface:** A warm off-white (#FAFAFA) prevents the interface from feeling clinical. 
- **AI Accents:** Subtle use of a deeper crimson gradient and star-gold (#FFD700) for high-tier ratings and "AI Recommended" badges.
- **Text:** High-contrast charcoal for headings to ensure legibility against warm backgrounds, with a softer grey-scale for secondary metadata.

## Typography

This design system utilizes **Plus Jakarta Sans** for its modern, friendly, and highly legible geometric terminals. 

- **Restaurant Names:** Set at 20-22px Semi-Bold to ensure they anchor the card components.
- **Body Copy:** Optimized at 15px with a generous 1.55 line-height to make long "AI Explanations" and reviews comfortable to read.
- **Labels:** Use Medium weight (500) to maintain hierarchy without the visual weight of Bold.
- **Currency:** The ₹ symbol should match the weight of the adjacent price value but can be sized 10% smaller to maintain visual balance.

## Layout & Spacing

The layout follows a **Fluid Grid** system based on an 8px base unit. 

- **Mobile:** A single column layout with 20px side margins. Cards should span the full width minus margins.
- **Desktop:** A 12-column grid with a max-width of 1280px. 
- **Rhythm:** Vertical spacing between restaurant cards should be 24px (stack-lg). Internal spacing within cards (e.g., between image and text) should be 12-16px to maintain a tight, grouped association.
- **Safe Areas:** Ensure bottom navigation bars on mobile account for "Home Indicator" areas while maintaining a fixed height of 64px.

## Elevation & Depth

This design system uses **Tonal Layers** combined with very soft **Ambient Shadows**.

1.  **Level 0 (Background):** The Warm Off-White (#FAFAFA) base.
2.  **Level 1 (Cards/Surface):** White (#FFFFFF) surfaces with a subtle 1px border (#F0F0F0) and a soft shadow (0px 4px 12px rgba(26, 26, 46, 0.05)).
3.  **Level 2 (Modals/Overlays):** Elevated surfaces with a more pronounced shadow (0px 12px 32px rgba(26, 26, 46, 0.12)).
4.  **AI Sections:** Use a "Glassmorphism" effect with a 12px backdrop blur and 80% opacity white fill to differentiate AI-generated insights from standard user reviews.

## Shapes

The design system adopts a **Rounded** language to feel approachable and modern.

- **Standard Radius:** 12px (0.75rem) for restaurant cards, images, and primary containers.
- **Input Fields:** 8px radius to feel slightly more structured.
- **Buttons:** 12px to match card containers for visual consistency.
- **Chips/Badges:** Pill-shaped (fully rounded) to contrast against the rectangular nature of the grid.

## Components

### Buttons
- **Primary:** Solid Red (#E23744) with White text. High-emphasis.
- **Secondary:** White background, 1px Border (#E23744), Red text. 
- **AI Action:** Subtle gradient background with a small "wand" icon prefix.

### Cards
- **Restaurant Card:** 12px corner radius. Top-half image (aspect ratio 16:9). Bottom-half white content area. Star ratings should be placed as an overlay on the image top-right corner with a semi-transparent dark background.
- **AI Insight Card:** Highlighted with a `surface_warm_gradient` and a subtle sparkle icon in the top-left header.

### Inputs
- **Search Bar:** Large, 12px radius, with a soft shadow. Includes "Bangalore" or city-context as a prefix label.
- **Checkboxes/Radios:** Rounded-sm (4px) for checkboxes, circular for radios. Always use Primary Red for active states.

### Chips
- **Cuisine/Filter Chips:** 14px Medium text. Unselected: Light grey border. Selected: Primary Red background or border.

### Feedback & Ratings
- **Star Ratings:** Use the Star-Gold (#FFD700) for filled stars. Scale of 1-5.
- **Price Indicators:** Represented as "₹₹₹₹" where active characters are Dark Charcoal and inactive are Light Grey.