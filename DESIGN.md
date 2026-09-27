---
version: alpha
name: Droidspaces
description: The visual language of droidspaces.org. Material 3 Expressive, derived from the Droidspaces Android app, for a static site on GitHub Pages.
colors:
  primary: "#a2cde2"
  on-primary: "#174557"
  primary-container: "#2d586a"
  on-primary-container: "#bfe9ff"
  secondary: "#b4cad6"
  secondary-container: "#2a3e48"
  on-secondary-container: "#adc3ce"
  tertiary: "#d1dcff"
  tertiary-container: "#becefa"
  on-tertiary-container: "#354569"
  error: "#fa746f"
  surface: "#0b0f11"
  surface-container-lowest: "#000000"
  surface-container-low: "#0f1417"
  surface-container: "#141a1e"
  surface-container-high: "#1a2124"
  surface-container-highest: "#1f272b"
  on-surface: "#dee7ec"
  on-surface-variant: "#a4acb2"
  outline: "#6e777c"
  outline-variant: "#41494e"
  primary-fixed: "#b5e0f6"
  primary-fixed-dim: "#a7d2e8"
typography:
  display-lg-emphasized:
    fontFamily: IBM Plex Sans
    fontSize: 57px
    fontWeight: 700
    lineHeight: 64px
    letterSpacing: 0px
  display-md-emphasized:
    fontFamily: IBM Plex Sans
    fontSize: 45px
    fontWeight: 700
    lineHeight: 52px
    letterSpacing: 0px
  headline-lg-emphasized:
    fontFamily: IBM Plex Sans
    fontSize: 32px
    fontWeight: 700
    lineHeight: 40px
    letterSpacing: 0px
  headline-md:
    fontFamily: IBM Plex Sans
    fontSize: 28px
    fontWeight: 400
    lineHeight: 36px
    letterSpacing: 0px
  title-lg:
    fontFamily: IBM Plex Sans
    fontSize: 22px
    fontWeight: 400
    lineHeight: 28px
    letterSpacing: 0px
  title-md-emphasized:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: 600
    lineHeight: 24px
    letterSpacing: 0.15px
  body-lg:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
    letterSpacing: 0.5px
  body-md:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: 400
    lineHeight: 20px
    letterSpacing: 0.25px
  label-lg-emphasized:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: 600
    lineHeight: 20px
    letterSpacing: 0.1px
  label-md:
    fontFamily: IBM Plex Sans
    fontSize: 12px
    fontWeight: 500
    lineHeight: 16px
    letterSpacing: 0.5px
  code:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: 400
    lineHeight: 22px
    letterSpacing: 0px
rounded:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  lg-increased: 20px
  xl: 28px
  xl-increased: 32px
  xxl: 48px
  full: 9999px
spacing:
  "50": 4px
  "100": 8px
  "150": 12px
  "200": 16px
  "300": 24px
  "400": 32px
  "600": 48px
  "800": 64px
  "1200": 96px
components:
  button-filled:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-lg-emphasized}"
    rounded: "{rounded.full}"
    height: 56px
    padding: 0 24px
  button-tonal:
    backgroundColor: "{colors.secondary-container}"
    textColor: "{colors.on-secondary-container}"
    typography: "{typography.label-lg-emphasized}"
    rounded: "{rounded.full}"
    height: 56px
    padding: 0 24px
  button-outlined:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-lg-emphasized}"
    rounded: "{rounded.full}"
    height: 56px
    padding: 0 24px
  card:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.xl}"
    padding: 24px
  card-nested:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 16px
  chip:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "{colors.on-surface}"
    typography: "{typography.label-lg-emphasized}"
    rounded: "{rounded.full}"
    height: 40px
    padding: 0 20px
  code-block:
    backgroundColor: "{colors.surface-container-lowest}"
    textColor: "{colors.on-surface}"
    typography: "{typography.code}"
    rounded: "{rounded.lg}"
    padding: 20px
  phone-frame:
    backgroundColor: "#0a0f12"
    rounded: "{rounded.xxl}"
    padding: 1.75%
---

# DESIGN.md

The visual language of droidspaces.org. It is derived from the Droidspaces Android app, whose own
[DESIGN.md](https://github.com/ravindu644/Droidspaces-OSS/blob/main/DESIGN.md) was read out of
`Android/app/src/main/java/com/droidspaces/app/`. The website is the app's design language taken
outdoors: same palette family, same flat surfaces, same restraint, plus the shapes and springs of
Material 3 Expressive that a marketing page has room for and a container manager does not.

Every number in this file has a source. Colour roles were generated from the app's dark primary
(`#7DC4E4`, Catppuccin Sky, `ui/theme/Color.kt`) with Google's `material-color-utilities` 0.4.0
on the 2025 colour spec. Radii, spacing, type sizes and the button press morph come from the token
files Google ships in `@material/web` 2.5.0 (`labs/gb/styles/`). Spring values come from the
Compose Material 3 `ExpressiveMotionTokens.kt`. Nothing here was picked by eye.

The front matter is the normative part. The prose says when each value applies.

## Overview

Droidspaces runs full Linux distributions on Android with a real init system, directly on the
phone's kernel. No emulation, no virtual machine, no Termux. The site exists to make that claim
in ten seconds to two audiences at once: a self-hoster with an old phone in a drawer, and a
kernel developer who will read the namespace list before believing anything.

The home page opens on the reason the project exists, not on the technology: an old phone
already has a battery, mobile data and a Linux kernel, so it can be a homelab that keeps running
when the power cuts. The kernel developer's claim (systemd as PID 1, no emulation) is the line
under it. Numbers on the page (release, stars, contributors) are stamped by the build from the
GitHub API, never typed.

The site has to feel like the Android app. Someone who installs the app after reading the site
should recognise it. That decides most of what follows: the same slate-blue palette, surfaces
that step up in tone rather than float on shadows, borders that carry state, and a companion app
that is flat by decision (55 sites set `tonalElevation = 0.dp`, zero card elevations in the tree).

Where the site differs from the app is where Material 3 Expressive gives it permission to. A
marketing page can afford one large shape, one spring, one moment of motion per section. The app
cannot, because it is a control surface. So the site is the app with the volume up one notch, not
a different product.

Personality, in three words: **native, calm, precise.** Not playful. Not enterprise. The tone of
someone who wrote the container runtime and is showing you it works.

The site is dark by default, because the app is, because terminals are, and because the phone
screenshots that carry every page were captured in dark mode. Light mode exists and is complete,
and it follows `prefers-color-scheme` unless the visitor overrides it with the toggle.

## Colors

Roles come from Material 3. The site uses the `--md-sys-color-*` custom property names exactly,
so the token file can be regenerated from the source colour without touching a stylesheet. The
only file that may contain a hex literal is `assets/css/tokens.css`.

The source colour is `#7DC4E4`, the app's dark primary. The scheme is `SchemeTonalSpot` on the
2025 spec, contrast level 0. Regenerate with the script in `scripts/tokens.mjs`, never by hand.

### Dark (default)

| Role | Value | Where it goes |
| --- | --- | --- |
| `primary` | `#a2cde2` | Filled buttons, the one accent per section, focus rings, active nav item |
| `on-primary` | `#174557` | Text and icons on `primary` |
| `primary-container` | `#2d586a` | Tinted surfaces that mean "running" or "active" |
| `on-primary-container` | `#bfe9ff` | Text on `primary-container` |
| `secondary` | `#b4cad6` | Restart, secondary actions, quiet emphasis |
| `secondary-container` | `#2a3e48` | Tonal buttons, selected chips |
| `tertiary` | `#d1dcff` | In-progress, downloading, the second decorative shape on a page |
| `tertiary-container` | `#becefa` | Decorative shapes only, never a button |
| `error` | `#fa746f` | Stop, failed, destructive. Nothing else. |
| `surface` | `#0b0f11` | Page background |
| `surface-container-lowest` | `#000000` | Code blocks and terminal panes |
| `surface-container-low` | `#0f1417` | Footer, the docs sidebar |
| `surface-container` | `#141a1e` | Cards sitting on the page |
| `surface-container-high` | `#1a2124` | Cards nested in cards, chips, table header row |
| `surface-container-highest` | `#1f272b` | Hover state of a `surface-container` card |
| `on-surface` | `#dee7ec` | Body text, headings |
| `on-surface-variant` | `#a4acb2` | Supporting text, metadata, captions |
| `outline` | `#6e777c` | Generated but unused. Outlined buttons take `outline-variant` so one border colour serves the site |
| `outline-variant` | `#41494e` | Card borders, dividers, table rules |
| `primary-fixed` | `#b5e0f6` | The phone mockups' accent. A fixed role barely moves between themes, so screenshots captured in dark mode still match in light mode |

### Light

| Role | Value |
| --- | --- |
| `primary` | `#28667e` |
| `on-primary` | `#f3faff` |
| `primary-container` | `#a8e2fe` |
| `on-primary-container` | `#0c536a` |
| `surface` | `#f7fafc` |
| `surface-container-lowest` | `#ffffff` |
| `surface-container-low` | `#eff4f8` |
| `surface-container` | `#e9eff3` |
| `surface-container-high` | `#e2e9ee` |
| `surface-container-highest` | `#dbe4e9` |
| `on-surface` | `#2b3438` |
| `on-surface-variant` | `#586065` |
| `outline-variant` | `#abb3b9` |

The full light set, including secondary, tertiary and error, lives in `tokens.css` and is
generated by the same script. It is not repeated here because nobody should be copying it by hand.

### How colour is used

**Borders and tint carry state. Fills stay quiet.** This is the app's rule and it is the site's.
A "running" container in a screenshot caption is not a green box. It is a normal card with an
accent border. The site never fills a card with `primary`.

**One accent per section.** Each section of a page gets one thing in `primary`: a button, or an
active tab, or a highlighted table cell. If a section has two things in `primary`, one of them is
wrong. Decorative shapes use `tertiary-container` or `secondary-container`, never `primary`, so
the eye still finds the button first.

**Terminals are black.** Code blocks and terminal panes sit on `surface-container-lowest`, which
is `#000000` in dark mode. This is the one place the site goes fully black, and it matches the
app's terminal, which does not follow the app theme either.

**Text alpha.** Secondary text is `on-surface-variant` at full opacity, not `on-surface` at 70%.
The M3 role already encodes the reduced contrast, and stacking alpha on it fails WCAG on
`surface-container-high`. Disabled text is `on-surface` at 38%, disabled fills at 12%, both from
the M3 state spec.

## Typography

One family for interface text, one for machine output. Nothing else.

**IBM Plex Sans** for everything a person wrote. It is the face of the project's own artwork,
it is released under the SIL Open Font License, and its plain, even strokes read as a technical
document rather than a consumer app. Self-host it from Fontsource as a single latin-subset
variable WOFF2 carrying the weight axis. Never load it from Google Fonts at runtime, because the
site should render with no third-party request.

**JetBrains Mono** for everything the machine wrote: commands, output, paths, unit names, kernel
version strings. This matches the app, where machine output is JetBrains Mono from
`ui/theme/Type.kt`. Self-hosted the same way.

The scale is the Material 3 type scale. The 2021 sizes are unchanged in Expressive; what changed
is the addition of *emphasized* styles, which take the same size and line height and bump the
weight. Here that step is 400 to 700 for display and headline styles and 400 to 600 for titles
and labels. Body copy stays at 400. The contrast between heavy headings and light body text is
the whole expressive signature, so nothing else is bold. The one exception is the product name
in the hero's sentence, set in `<strong>` so the eye finds what the sentence is about.

| Element | Style | Notes |
| --- | --- | --- |
| Hero headline | `display-lg-emphasized` | 57/64, weight 700. Drops to `display-md-emphasized` under 600px |
| Hero headline, 840 to 1199 | `display-md-emphasized` | The 5/12 column is too narrow for 57px there |
| Section headline | `headline-lg-emphasized` | 32/40, weight 700. A claim of three to six words |
| Card title | `title-md-emphasized` | 16/24, weight 600 |
| Section intro paragraph | `title-lg` | 22/28, weight 400, `on-surface-variant` |
| Body copy | `body-lg` | 16/24 |
| Supporting text, captions | `body-md` | 14/20, `on-surface-variant` |
| Button and chip label | `label-lg-emphasized` | 14/20, weight 600 |
| Table header, metadata | `label-md` | 12/16, weight 500 |
| Code, terminal, commands | `code` | JetBrains Mono 14/22 |

Line length is capped at 68 characters for body
copy (`max-width: 68ch`), which is where a 16px sans stays comfortable. Headlines do not track
tighter than 0; letter-spacing of −2px on a display headline is a web-template habit, not a
Material one.

Every section opens the same way: a short claim as the headline, one `title-lg` sentence under it,
and chips for any list of facts. A second paragraph is the exception, not the pattern; if the
section needs one, the claim is probably too vague.

Never accent a single word of a headline in colour or italic. The headline is one sentence in one
colour. Emphasis, when needed, is the sentence break.

## Layout

The grid unit is 8px. The spacing scale is the Material 3 space token set, of which the site uses
nine steps: **4, 8, 12, 16, 24, 32, 48, 64, 96**. If a gap wants 40, it wants 32 or 48.

| Gap | Value |
| --- | --- |
| Icon to its label, chip to chip | 8 |
| Between rows inside a card | 12 |
| Card inner padding | 24 |
| Between cards in a grid | 16 |
| Section inner padding, top and bottom | 96 on desktop, 64 under 840px |
| Page side gutter | 24 on desktop, 16 under 600px |
| Content max width | 1200px |
| Prose max width | 68ch |

Breakpoints are the Material window size classes and nothing else: **600, 840, 1200, 1600**.
Compact is under 600, medium to 839, expanded to 1199, large to 1599. Layouts collapse at those
lines, not at 768 or 1024.

The hero is a two-column split at expanded and above: copy on the left at 5/12, phone mockup on
the right at 7/12, vertically centred. Under 840 it stacks, copy first, and the phone takes 80% of the column
and the shape behind it 120%, so the shape still frames the phone on both sides. At 840 and up a
shape is never wider than its own column. It sits at `z-index: -1` inside a phone stage that sets
`isolation: isolate`, so it stays behind the phone and never over copy. The section itself is
not isolated: a phone shadow has to cross into the next section, and a section that isolates
cuts it off in a hard line; `main` clips
horizontal overflow so it can never scroll the page either.

The home page has six sections: the hero, init and services, the home server, the app carousel,
the comparison, and requirements with the download.

Feature sections alternate the side the phone sits on. Text, then phone; phone, then text. This
replaces the row of six identical cards.

The page background is one unbroken `surface`. Sections carry the 1200px measure in their side
padding and have no fill of their own. Alternating tonal bands were tried and removed: at every
band edge the eye reads a separator line, and the page stops feeling like one surface.

Cards appear in one place: the comparison against PRoot, chroot and QEMU, where a table is the
honest format and cards would hide the comparison. Everywhere else, content sits directly on the
page background with a headline, a paragraph and a screenshot.

The docs pages are a two-column layout: a 280px sidebar on `surface-container-low` with the page
tree, and a prose column. The sidebar becomes a top drawer under 840px.

## Elevation & Depth

There are no shadows on this site, with one exception.

Depth is tonal. A card on the page is `surface-container`. A card inside it is
`surface-container-high`. Hovering a card steps it to `surface-container-highest`. That is the
whole elevation system, and it is the app's: depth is expressed by stepping the surface colour up
one level and drawing a 1px border.

Every card and every nested surface has a 1px border in `outline-variant`. On the app the alpha
of that border drifted across 40 sites; on the site it is one value, full opacity, because
`outline-variant` in M3 is already the low-contrast outline.

The exception is the phone mockup. It carries `0 40px 90px rgba(0,0,0,.55)` (`--shadow-phone`), because it is a
photograph of an object, not a surface of the page, and an object sitting on a page has a shadow.
No other element may have one. If a card looks like it needs a shadow, it needs a higher surface
tier.

Nothing is glassmorphic. `backdrop-filter` is used once, on the sticky navigation bar, at
`blur(16px)` over `surface` at 80% opacity, which is the Android 16 shade behaviour. It is not a
card style.

## Shapes

The radius scale is Google's, from `md-shape-tokens.css`, and the three larger values are the
ones Expressive added: **4, 8, 12, 16, 20, 28, 32, 48, full.**

| Element | Radius |
| --- | --- |
| Card on the page | 28 (`xl`) |
| Card nested in a card, code block | 16 (`lg`) |
| Chip, badge | full |
| Button at rest | full |
| Button pressed | 12 (`md`) |
| Button, selected or toggled | 16 (`lg`) |
| Text input | 16 |
| Phone frame outer | 7.8% of the frame width |
| Phone screen | 6.2% of the frame width |
| Decorative shapes | see below |

**Buttons morph when pressed.** A resting button is a pill. On `:active` it snaps to 12px corners
and springs back on release, over `350ms cubic-bezier(0.42, 1.67, 0.21, 0.9)`. That curve and
those numbers are Google's own, from the expressive button in `@material/web` 2.5.0, and the
overshoot in the bezier is the point. Do not replace it with `ease-out`.

**Decorative shapes are the one expressive flourish per page.** Material 3 Expressive ships 35
named shapes. The site uses five: `cookie-12`, `cookie-9`, `clover-4`, `sunny` and `pill`. Each appears at
most twice on a page, as a `mask-image` over a flat `tertiary-container` or `secondary-container`
fill, sitting behind a phone mockup. Every single-phone stage on the home page has one, each shape
used once; the carousel has none, because three overlapping phones leave only slivers of it,
which read as a rendering fault, `tertiary-container` and `secondary-container` alternating. They are large (400 to 1000px), slow to move (see
Motion), and never carry text or icons. They are never `primary`. The SVG masks live in
`assets/shapes/` and come from Beer CSS 5 (MIT), which traced them from Google's Figma kit.

The phone frame is its own shape and it is fixed: bezel at 1.75% of the frame width, outer radius
7.8%, screen radius 6.2%, a centred punch-hole camera at 5.2% of the screen width, in the bezel
colour, with nothing drawn inside it. Frame colour `#0a0f12` (`--phone-frame`). The screenshots stop at
the app's title bar, so the mockup draws a status bar (time, camera, signal icons) and a gesture
bar around them in the app's own surface colours (`--phone-app-surface`, `--phone-app-bar`,
`--phone-app-on-surface`). This is a Galaxy S25 Ultra
silhouette, thin and square, and it is the same on every page at every size. Screenshots inside
it are `object-fit: cover; object-position: top`.

Where Chromium supports it, cards and buttons take `corner-shape: squircle` inside an `@supports`
block, which is the true Material shape. Browsers without it get the round corner. Nothing
depends on the difference.

## Components

Components are plain HTML with classes. No web component library, no framework. The Lit-based
`@material/web` components are in maintenance mode and predate Expressive, so they are not used;
their token stylesheets are.

### Buttons

Height 56px (M3 `md` size). Three variants and no more:

| Variant | Fill | Text | Border |
| --- | --- | --- | --- |
| Filled | `primary` | `on-primary` | none |
| Tonal | `secondary-container` | `on-secondary-container` | none |
| Outlined | transparent | `on-surface-variant` | 1px `outline-variant` |

A section has one filled button. "Download" is filled. "Read the docs" beside it is outlined.
Two filled buttons next to each other is the tell of a template.

Labels are `label-lg-emphasized`, one line, sentence case. "Download for Android", not "DOWNLOAD
NOW". No arrow glyph appended to the label; the button is already the arrow.

Icons inside buttons are Material Symbols Rounded, 20px, `FILL 0` at rest and `FILL 1` on hover,
animated over the effects spring. The icon leads the label.

### Chips

Height 40px, full radius, `surface-container-high` fill, 1px `outline-variant` border,
`label-lg-emphasized`. Used for lists of facts: init systems, supported architectures, what a
container can run, the hardware the app hands over. Every chip names something documented in the
main repository's README or `Documentation/Features.md`; a chip that could describe any product
("Docker inside", "Fast") is not a fact. A selected chip, and any chip under the pointer, takes `secondary-container` with
`on-secondary-container` text. Chips wrap; they do not
scroll horizontally.

### Cards

`surface-container`, radius 28, 1px `outline-variant`, padding 24. Title in `title-md-emphasized`,
body in `body-md`. A card never contains a button unless the card is the download card. Hover
steps the surface to `surface-container-highest` over the effects spring, with no transform, no
lift, no shadow.

### Code blocks and terminal panes

`surface-container-lowest`, radius 16, padding 20, JetBrains Mono. A copy button sits top-right
as an icon button. Where a terminal transcript appears it is a real `<pre>`, not an image, with
prompt in `primary`, output in `on-surface`, and the cursor block static. It does not type itself
out. The hero has no terminal pane: the phone screenshot already shows the runtime working, and a
boot transcript beside it repeated the next section.

### Navigation

Sticky, 64px tall, `surface` at 80% with `backdrop-filter: blur(16px)`, a 1px `outline-variant`
bottom border that appears only once the page has scrolled. Logo mark left, links right, theme
toggle last. The active link is `primary`; the rest are `on-surface-variant`. Under 840px the
links collapse into a full-height drawer from the right, on `surface-container-low`.

### Phone mockup

One component, one silhouette, described under Shapes. It takes a screenshot. Phones do not
float: an idle loop on a phone beside a turning shape drifts out of step with it and reads as a
glitch, so the shape is the only thing that keeps moving.

Three phones in a group form the app carousel, one `<figure>` each with a one-line `body-md`
caption saying what the screen does. Exactly one phone is in front and only its caption shows.

- On a wide pointer screen (`hover: hover`, 840 and up) the phones overlap, the side ones at 80%
  scale. Hovering or keyboard-focusing a phone brings it to the front; at rest the middle one is.
  Hover wins over focus, so two phones are never in front at once.
- Everywhere else the group is a horizontal scroll-snap carousel, edge to edge under 840, opening
  on the middle screen. A scroll-driven `view(inline)` timeline makes the centred phone full size
  and its neighbours 85%, and shows only the centred caption.

No JavaScript runs either mode.

### Tables

The comparison table is `surface-container` with a `surface-container-high` header row, 1px
`outline-variant` rules, `label-md` headers, `body-md` cells. The Droidspaces column is tinted
`primary-container` at 20%, which is the only fill of `primary` on the page and is why the
comparison section has no filled button.

### Footer

`surface-container-low`, three columns on desktop (project, community, legal), the logo mark and
a one-line description, GPLv3, and the maintainer's name. No newsletter box.

## Motion

Material 3 Expressive replaced duration-and-easing with springs. Two families: **spatial** springs
move, resize and reshape things, and may overshoot; **effects** springs change colour and opacity
and never overshoot. The site uses the Expressive spatial set and the shared effects set, encoded
as CSS `linear()` easings generated from the Compose damping and stiffness values. No JavaScript
animation library.

| Token | Damping / stiffness | Settles in | Use |
| --- | --- | --- | --- |
| `--motion-spatial-fast` | 0.6 / 800 | 480ms | Button press, chip select, icon fill |
| `--motion-spatial-default` | 0.8 / 380 | 470ms | Cards and phones entering the viewport, drawer open |
| `--motion-spatial-slow` | 0.8 / 200 | 640ms | The hero phone's arrival, section shapes |
| `--motion-effects-fast` | 1.0 / 3800 | 180ms | Hover colour, focus ring |
| `--motion-effects-default` | 1.0 / 1600 | 270ms | Surface tier step on hover, theme change |

The `linear()` point lists are in `tokens.css`, along with `--motion-press` for the button morph
and `--motion-float`, which is generated but unused since phones stopped floating. They were produced from the spring equation, not
drawn, so `--motion-spatial-fast` really does overshoot by 9.5% and settle, the way the Android
button does.

**Five kinds of motion exist on the site, and nothing else moves:**

1. **Arrival.** When a phone mockup or decorative shape enters the viewport, it translates up 24px
   and fades in over `--motion-spatial-default`, once. Text does not animate in. Cards do not
   animate in. Only the objects. The section's headline is already there when you get to it.
2. **Press and hover.** Buttons morph on press. Surfaces step a tier on hover. Chips take
   `secondary-container` on hover. Icons fill. All use the springs above.
3. **Carousel.** A phone promoted by hover or focus scales to 100% over
   `--motion-spatial-default`; its caption fades over `--motion-effects-default`. In the swipe
   carousel the scale and caption follow the scroll position, not a timer. When the overlapping
   group arrives, the side phones fan out from behind the front one over the same `view()` range
   as arrival.
4. **Shape turn.** Decorative shapes turn once every 120 seconds, linear, forever, the way the
   M3 Expressive loading indicator they come from turns. `secondary-container` shapes turn the
   other way, so neighbours never look like one pattern. The turn runs on a timer, not on scroll,
   so the page keeps moving while the visitor reads. A shape arrives by fading in from 90% scale
   rather than by translating, because its translate is what centres it.
5. **Shape morph.** The loading indicator on the downloads page cycles through `cookie-12`,
   `clover-4` and `sunny` by morphing the mask, which is the M3 Expressive loading indicator.
   Nothing else morphs.

Scroll-driven animation (`animation-timeline: view()`) drives the arrival where supported, with
`@starting-style` as the fallback. Nothing is hidden until an animation fires: the page renders
complete with JavaScript disabled and with `prefers-reduced-motion: reduce`, in which case the
shape turn stops, arrival becomes an instant fade, the button morph is disabled, the
carousel loses its fan-out and scale (it still swipes and still hovers, instantly), and the swipe
carousel shows every caption. The reduced-motion
branch is not optional.

There is no float, no parallax, no marquee, no typing effect, no counter that counts up, no pulsing dot, no
cursor that blinks, no hover transform that scales or rotates an image, and no page-load sequence
that stagger-reveals every element in turn. Each of those is a template tell and each has been
seen on a hundred landing pages this year.

## Do's and Don'ts

Do use `primary` on exactly one element per section.
Do give every card a 1px `outline-variant` border and no shadow.
Do let the phone mockups carry the page. They are real screenshots of a real app.
Do write headlines as one plain sentence in one colour.
Do keep body copy at `body-lg` and under 68 characters a line.
Do run the site with JavaScript off before every release and confirm nothing is missing.
Do test `prefers-reduced-motion` and `prefers-color-scheme` on every page.
Do keep a 48px minimum on anything tappable. This is the one rule design does not override.

Don't use a gradient anywhere: not on a background, not on text, not as a glow behind a phone.
Don't use a colour that is not in `tokens.css`.
Don't put an uppercase, letter-spaced label above a heading.
Don't number sections 01, 02, 03. Nothing on the site is a sequence except the install steps.
Don't join metadata with middle dots. Use a comma or a separate line.
Don't append an arrow to a link or button label.
Don't use an em dash. Use a comma, a full stop, or rewrite the sentence.
Don't write "Unlock", "Supercharge", "Seamless", "Blazing fast", "Next-generation" or "Reimagine".
Don't build a row of three or six identical icon-title-text cards.
Don't animate text, and don't animate anything on scroll except arrival and the swipe carousel.
Don't add a second shadow, a glow, a frosted card, or a dot grid background.
Don't load a font, icon or script from a third-party origin at runtime.

## Decided exceptions

Looked at, deliberately left alone. Do not re-open these without a reason the original one misses.

- **The phone mockup has a shadow.** It is the only shadow on the site. It is an object, not a
  surface, and the same silhouette is used in the LinkedIn and README artwork, so the two must
  match.
- **Terminal panes go to `#000000` in dark mode** rather than a tonal surface. The app's terminal
  does the same, and a slate terminal reads as a disabled one.
- **`primary-fixed` is used for accents inside the phone screenshots' frames**, so the mockups look
  the same in light mode. A screenshot captured in dark mode cannot change with the theme, and a
  fixed role is what M3 provides for that case.
- **The navigation bar is the one `backdrop-filter`.** It follows the Android 16 shade. A second
  use anywhere turns the site into a glassmorphism template.
- **The docs pages keep their generated structure** from `.github/scripts/build-docs.py` and only
  restyle it. The Markdown source is in the main repository, and the site must not fork it.
- **Light mode was generated, not designed.** It is the same source colour through the same
  scheme. If a light-mode surface looks wrong, fix the generator input, not the CSS.
