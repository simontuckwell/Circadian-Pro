
<p align="center">
  <img src="custom_components/circadian_pro/logo.png" alt="Circadian Pro" width="220">
</p>

<h1 align="center">Circadian Pro</h1>

<p align="center">
  Advanced circadian lighting control for Home Assistant.
</p>

## Overview

Circadian Pro automatically adjusts the brightness and color temperature of your lights throughout the day according to sunrise, sunset and your configured preferences.

It supports multiple independent instances, manual-control detection, automatic sleep mode, calibrated RGB/RGBW/RGB+CCT lighting and several brightness-transition profiles.

**Current stable version:** `0.21.32`

**Available in the HACS default catalog.** Search for **Circadian Pro** to install it. Version 0.21.32 updates the installation and upgrade guide following [catalog approval](https://github.com/hacs/default/pull/11948); lighting behavior and the complete English/Spanish interface are unchanged from 0.21.31. See the [release notes](docs/release-0.21.32.md).

[Installation](#installation) · [Instalación en español](#instalación-en-español) · [Updating](#updating) · [Screenshots](#screenshots)

## Screenshots

The actual Circadian Pro panel, shown with fictional profiles and lights. These examples use demonstration solar times in UTC; your installation uses Home Assistant's location and time zone.

**Profiles:** create a profile or open its settings and calibration from one compact list.

![Circadian Pro profile list with a configuration button for each example profile](docs/images/profiles.jpg)

**Brightness and color temperature:** preview the daily curve, sunrise and sunset, and the effect of your transition windows and sleep schedule.

![Brightness and color-temperature settings with the interactive daily curve](docs/images/daily-curve.jpg)

**Calibration:** adjust RGB and white channels using sliders or numbers. Light preview is optional.

![RGB and dual-white calibration controls at the neutral 4000 K reference](docs/images/calibration.jpg)

**On mobile:** the same panel adapts to a narrow screen. This example shows the Spanish interface.

<img src="docs/images/mobile-es.jpg" alt="Spanish Circadian Pro profile list on a mobile-sized screen" width="390">

## Languages

The panel, configuration forms, help texts, selectors, validation messages and actions support **English and Spanish**. The panel follows **your Home Assistant interface language**, including regional variants such as `es-MX` and `en-GB`; unsupported languages fall back to English. Changing language refreshes the panel's translations without discarding unsaved settings.

Native switch names are translated using Home Assistant's **server language**, as required by its entity naming system. Profile names, light names and any names you have customized stay as you entered them. Entity IDs, YAML keys and action identifiers remain stable for existing automations; diagnostic logs retain their technical messages. GitHub's README is separate from Home Assistant and does not change language automatically.

**En español:** el panel, los formularios, las ayudas, los selectores, los mensajes de validación y las acciones están disponibles en español e inglés. El panel sigue el idioma de tu interfaz y actualiza sus textos sin perder los ajustes pendientes. Los nombres nativos de los interruptores siguen el idioma del servidor de Home Assistant. Se conservan los nombres que hayas elegido y todos los identificadores que utilizan tus automatizaciones.

## Features

- Automatic brightness and color-temperature adaptation.
- Multiple independent Circadian Pro instances.
- Natural, Linear and Sigmoid brightness modes, with optional shared color-temperature timing in Linear and Sigmoid.
- Transition windows with synchronized sliders and editable whole numbers from 0 to 240 minutes. Both windows can be zero for a step in the target at sunrise and sunset. Existing values are preserved exactly; YAML and service durations retain their seconds-based format.
- One interactive curve showing how the selected mode and the two windows affect the transition around sunrise and sunset. Natural hides the two unused windows and shows its own curve.
- Manual and automatic sleep mode.
- Sunrise and sunset offsets in minutes in the settings UI. Existing values convert automatically: 3600 seconds appears as 60 minutes. YAML and service values keep their existing seconds-based format.
- Fixed or limited sunrise and sunset times.
- Manual-control detection with optional automatic reset.
- RGB, RGBW, RGB+CCT (`rgbww`) and color-temperature light support.
- Custom RGBW and RGB+CCT calibration at 4000 K and 1000 K.
- Configurable adaptation intervals and transitions.
- Interception of `light.turn_on` and `light.toggle`.
- Home Assistant services for applying settings and managing manual control.

## Installation

### Requirements

- Home Assistant **2026.10.0 or newer**.
- An **administrator account** to set up the integration and use its sidebar panel.
- Lights already configured and working in Home Assistant. The available color controls depend on each light's capabilities.
- Home Assistant's location and time zone set correctly for sunrise and sunset calculations.

### Install from the HACS catalog — recommended

1. Open **HACS**, search for **Circadian Pro**, and open its page.
2. Select **Download** and choose the latest stable release.
3. Restart Home Assistant.
4. Complete the one-time setup below.

If your Home Assistant version uses standalone HACS and it is not installed, follow its [official setup guide](https://www.hacs.xyz/docs/use/) first. Circadian Pro is already in its default catalog; adding a custom repository is optional.

**Using the built-in Marketplace?** HACS documents this installation route for Home Assistant 2026.11 and newer. Search for **Circadian Pro** in **Settings → Marketplace**, following the [official Marketplace guide](https://www.hacs.xyz/docs/marketplace/). Continue with the setup below if it has not already opened. A first installation through Marketplace can open setup without a restart; follow any restart prompt shown by Home Assistant. The HACS steps above apply to the standalone HACS interface.

### Activate the panel and create your first profile

1. Open **Settings → Devices & services → Add integration**.
2. Search for **Circadian Pro** and select it once. This activates the panel; it does not ask you to configure lights yet.
3. Open **Circadian Pro** in the sidebar and choose **Create first profile**.
4. Name the profile, select its lights, and follow the settings and calibration steps. White-channel settings appear automatically for compatible RGBW or RGB+CCT lights.
5. Choose **Finish** to save the settings. **Preview light** is optional and changes the selected lights only while preview is active.

The sidebar panel is added automatically for administrator users. No YAML, dashboard card or manual sidebar link is needed. Downloading the files through HACS alone does not complete this one-time setup.

Use **New profile** in the panel to add more profiles. Each profile has its own settings button, lights and calibration. Changes refresh automatically, and profiles can be sorted by name or recent modification. See [calibration and controls](#rgbw-and-rgbcct-calibration) for details.

### Cannot find it? Custom repository fallback

Catalog changes can take up to eight hours to reach HACS, according to its [inclusion notice](https://github.com/hacs/default/pull/11948#issuecomment-6624872063). If Circadian Pro is still absent from your standalone HACS search:

1. Open **HACS → ⋮ → Custom repositories**.
2. Enter `https://github.com/K320X/Circadian-Pro`, select **Integration**, and choose **Add**.
3. Search for Circadian Pro again, download it, restart Home Assistant and complete the one-time setup above.

This installs the same project and releases. See the [official custom-repository instructions](https://www.hacs.xyz/docs/faq/custom_repositories/). Marketplace has its own repository-link installation flow, described in the [Marketplace guide](https://www.hacs.xyz/docs/marketplace/).

### Manual installation — alternative without HACS

1. Download the **`circadian_pro.zip` asset** from the [latest release](https://github.com/K320X/Circadian-Pro/releases/latest).
2. Extract it and copy the resulting `circadian_pro` folder into `/config/custom_components/`, creating `custom_components` if necessary.
3. Check that `manifest.json` is directly inside `/config/custom_components/circadian_pro/`, without an extra nested `circadian_pro` folder:

```text
/config/custom_components/circadian_pro/
├── __init__.py
├── manifest.json
├── config_flow.py
├── switch.py
└── ...
```

4. Restart Home Assistant and follow [Activate the panel and create your first profile](#activate-the-panel-and-create-your-first-profile).

### Instalación en español

Necesitas **Home Assistant 2026.10.0 o posterior**, una cuenta de administrador y luces que ya funcionen en Home Assistant. Comprueba también la ubicación y la zona horaria: se utilizan para calcular el amanecer y el atardecer.

**Instalación recomendada desde el catálogo:**

1. Abre **HACS**, busca **Circadian Pro** y entra en su ficha.
2. Pulsa **Descargar**, selecciona la última versión estable y reinicia Home Assistant.
3. Ve a **Configuración → Dispositivos y servicios → Añadir integración**, busca **Circadian Pro** y selecciónalo una vez.
4. Abre **Circadian Pro** en la barra lateral y pulsa **Crear primer perfil**.
5. Ponle un nombre, selecciona las luces y completa los ajustes y la calibración. Pulsa **Terminar** para guardar. **Previsualizar luz** es opcional y permite ver los ajustes en las luces mientras está activado.

Si tu versión de Home Assistant usa HACS independiente y aún no lo tienes instalado, sigue su [guía oficial de instalación](https://www.hacs.xyz/docs/use/). Si tu versión dispone del **Marketplace integrado** —la vía documentada para Home Assistant 2026.11 y posteriores—, busca Circadian Pro en **Configuración → Marketplace** y sigue la [guía oficial](https://www.hacs.xyz/docs/marketplace/). Después completa la configuración inicial si no se ha abierto automáticamente y reinicia cuando Home Assistant lo indique.

El panel lateral aparece automáticamente para administradores después de añadir la integración. No necesitas YAML ni crear un enlace manual. Los siguientes perfiles se añaden desde **Nuevo perfil** en el propio panel.

**Si no aparece en HACS:** la incorporación al catálogo puede tardar hasta ocho horas en propagarse. Como alternativa, abre **HACS → ⋮ → Repositorios personalizados**, añade `https://github.com/K320X/Circadian-Pro` con tipo **Integración**, y continúa desde el paso de descarga. Es el mismo proyecto y recibe las mismas versiones.

**Instalación manual:** descarga el archivo `circadian_pro.zip` de la [última publicación](https://github.com/K320X/Circadian-Pro/releases/latest), descomprímelo y copia su carpeta `circadian_pro` en `/config/custom_components/`. Reinicia Home Assistant y continúa desde **Añadir integración**. La ruta final del manifiesto debe ser `/config/custom_components/circadian_pro/manifest.json`.

## Updating

### Installed through HACS or Marketplace

New stable releases are published on [GitHub](https://github.com/K320X/Circadian-Pro/releases). HACS or Marketplace checks for releases and makes available updates visible in Home Assistant.

1. Open the Circadian Pro update in HACS, Marketplace or Home Assistant's update list.
2. Read the release notes and create a Home Assistant backup before installing.
3. Install the update and restart Home Assistant when prompted so the new integration code loads.
4. Open the Circadian Pro panel and check your existing profiles. You do not need to add the integration again.

Profiles and calibrations are stored in Home Assistant's configuration. Updating the integration is intended to preserve them, together with entity identifiers and switch states. Circadian Pro does not download or install its own updates. Updates replace the component files; Home Assistant backups are managed separately.

**Already installed through a custom repository?** Keep using the existing installation. Catalog inclusion does not require reinstalling Circadian Pro or recreating its integration entries or profiles.

**Moving from a manual installation to HACS?** Back up first, find Circadian Pro in the catalog and download it. Keep your existing integration entries and profiles. HACS manages the same `custom_components/circadian_pro` directory after installation; use the custom-repository fallback only if the catalog search does not find it.

### Installed manually

1. Create a Home Assistant backup and download `circadian_pro.zip` from the new release.
2. Replace `/config/custom_components/circadian_pro/` with the extracted `circadian_pro` folder. Keep the existing integration entries and profiles in Home Assistant.
3. Restart Home Assistant and check your profiles in the sidebar panel.

**En español:** abre la actualización de Circadian Pro en HACS, Marketplace o la lista de actualizaciones de Home Assistant. Lee las notas, crea una copia de seguridad, instala y reinicia cuando se indique. No vuelvas a añadir la integración ni borres perfiles: se reutiliza la configuración existente. Si ya lo instalaste mediante un repositorio personalizado, puedes seguir utilizándolo; entrar en el catálogo no requiere reinstalar. Para actualizar manualmente, sustituye la carpeta del componente por la del nuevo ZIP y reinicia, conservando las entradas de integración.

### Panel missing or showing an older version?

- **No sidebar entry:** sign in as an administrator and check that Circadian Pro has been added under **Settings → Devices & services**. Downloading the files alone is not enough with standalone HACS.
- **A separate Circadian Pro entry appears alongside your profiles:** this entry keeps the sidebar panel available, even when there are no lighting profiles. It does not create lights or switches and should be kept.
- **Old interface after an update:** complete the required restart, then reload the frontend as described below.

Each panel script and its custom element now have identities based on the script's contents, so Home Assistant can load the updated interface without reusing an older panel implementation. If a view still shows the old interface after updating, reload the Home Assistant frontend. In the iOS Companion app, a persistent old view can be refreshed from **Settings → Companion App → Debugging → Clear web view cache** (called **Reset frontend cache** in older versions), followed by closing and reopening the app.

## RGBW and RGB+CCT calibration

The 4000 K and 1000 K calibration points are visual references. Adjust RGB and white intensity at each point to get the appearance you want. They are separate from the physical temperatures of the white LEDs.

Each calibration channel has a colored slider and an editable number that stay in sync. RGB tracks run from black at 0 to the full channel color at 255; white intensity runs from black to white. The RGB+CCT white-mixture slider runs from the configured warm white temperature (left) to the cold white temperature (right), with a warm, neutral-white and cool-blue gradient as a visual guide. You can go back from the final 1000 K step without saving; only **Finish** saves the configuration. Light previews remain opt-in.

For RGBW, `white_w_kelvin` remains the temperature of the single white channel, with a default of 3000 K. For RGB+CCT lights that announce `rgbww`, the same value describes the warm white (WW) LED. The extra `white_cw_kelvin` setting describes the cold white (CW) LED. If omitted, Circadian Pro uses the light's maximum color temperature, or 6500 K when unavailable. In the panel, warm white appears on the left and cold white on the right, with their descriptions below; narrow screens stack the two fields.

At the 4000 K reference, RGB+CCT has three independent adjustments: RGB channels, total white intensity, and white mixture temperature (`cal_white_kelvin_neutral`). The mixture splits the white intensity between WW and CW and must stay between their physical temperatures. If omitted, it uses 4000 K clamped to that range. The 1000 K reference keeps its RGB and white-intensity controls; warm white fades so RGB can produce the warm/orange appearance below the physical WW temperature.

The extra cold-white and mixture controls appear only when a selected light supports `rgbww`. RGBW keeps one white channel; profiles containing only RGB lights skip physical-white settings and show only RGB calibration. Existing hidden white values are preserved. Pixel-addressable (IC) control is independent of whether an entity exposes RGB, RGBW, or RGBWW.

Open the **Circadian Pro** sidebar panel to create profiles or configure and calibrate existing ones. **New profile**, centered below the table, asks for a name and creates an empty profile before opening its configuration wizard. Creating an empty profile does not control any lights. If you close the configuration wizard, the created profile remains available so you can finish configuring it later. The profile list updates automatically when profiles are added, removed, renamed, configured or loaded, including changes made from Home Assistant's integration page. Updates preserve any configuration draft.

General settings are grouped into adaptation timing, brightness and temperature, sleep mode, sunrise and sunset, manual changes, and compatibility. Related settings share a row on wide panels and stack on narrow screens, with each description kept beside its own control. All settings remain available.

The sidebar uses a sun-and-moon icon. The profile-list header has a **Go to integration** shortcut to Circadian Pro's native Home Assistant page, where profile devices, switches and entity IDs are available. While editing, the header retains **Close without saving**. On narrow screens, the panel header provides a button to open Home Assistant's sidebar; it stays hidden on desktop. Primary buttons use the theme's background color for readable text in both light and dark themes.

On the native integration page, the settings button for a loaded profile opens that profile directly in the Circadian Pro panel. The settings button on the separate **Circadian Pro** panel entry opens the profile list. A link to an unavailable or deleted profile also returns to the list. Switching profiles through these links closes the previous wizard without saving its draft and stops any active light preview before opening the next profile. Home Assistant's **Add entry** button and the separate panel entry remain in place.

The preview checkbox is disabled by default. Checking it applies the draft immediately; adjusting RGB or white controls while it is checked updates the lights without saving. Unchecking it stops the preview and restores the previous state.

The panel includes general settings, physical white channels, and both calibration points. The first step has **Next**; intermediate steps have **Back** and **Next**; the final step has **Back** and **Finish**. Only **Finish** saves the settings. Going back preserves your draft. Navigation stops the preview, so each calibration step starts with it disabled. Canceling or closing the panel also stops the preview; the 60-second expiry stops it and clears the checkbox automatically. A light changed manually during the preview keeps the external change. The panel uses Home Assistant's existing options flow to validate and save settings.

## Brightness / temperature modes

Color temperature normally follows its own solar curve, reaching its maximum around solar noon. In Linear or Sigmoid mode, **Also apply to color temperature** (`apply_temperature_curve`, default `false`) makes brightness and Kelvin follow the same progress between their respective configured limits. The checkbox is hidden in Natural mode, which ignores it. Existing profiles keep their previous behavior until you enable the option.

The panel displays one interactive curve below the mode controls. It updates while dragging either time slider or editing its number, without saving settings or changing lights. Each active window accepts 0–240 whole minutes. Equal windows place the midpoint at sunrise and sunset; unequal windows move more of the transition before or after the events. Natural hides both duration controls as well as the temperature checkbox, retaining their draft values when you switch back.

The graph uses the current day and time zone configured in Home Assistant. Sunrise and sunset are positioned at their actual effective times, displayed below their labels; fixed times, offsets and earliest/latest limits are included. Two additional clock references mark the elapsed-time midpoint between sunrise and sunset and between sunset and the following sunrise. These arithmetic references do not change the astronomical solar noon and midnight used by the curves. Daylight-saving days retain their real duration. Solar and automatic-night schedule drafts update the chart without saving or controlling lights. The day refreshes when the form opens, at the next local midnight and after resuming a suspended page. If schedule data cannot be calculated or loaded, the chart shows an explicit status instead of invented times.

Without automatic sleep mode, minimum/maximum brightness bounds remain normalized, so the graph stays useful when the profile’s minimum and maximum brightness are equal. An orange-to-white background represents normalized color temperature: orange marks its minimum and white its maximum. Without shared timing, and always in Natural mode, it follows the independent daytime solar curve and remains orange at night. With shared timing in Linear or Sigmoid, it follows the chosen curve and windows, including sharp target changes when both windows are zero.

Automatic sleep mode is drawn on this same graph. During its solar or scheduled window, the line uses the configured sleep brightness and the background uses the selected sleep RGB or an illustrative Kelvin color. Brightness is then plotted on a real 0–100% scale, including when the normal minimum and maximum are equal. Schedule boundaries have dotted red lines and start/end labels beneath the graph. Entry and exit fades illustrate the general transition duration at the nominal boundary; the transition information explains that actual application waits for an adaptation cycle and depends on light support. It does not predict manual sleep-switch changes, measured light output, calibrated LED appearance or the exact interpolation performed by each device. The visible caption stays brief, details remain accessible by keyboard or touch, and the curve stays about one third shorter on mobile.

The update does not migrate or clamp saved durations. A legacy duration above 240 minutes remains unchanged and can still be retained while Natural ignores it; selecting Linear or Sigmoid in the panel exposes that value and requires reducing it to the supported UI range before saving. Canonical YAML and service durations retain their previous validation.

Minute fields, including sunrise/sunset offsets, display whole numbers. Older seconds-based values are shown rounded to the nearest minute, without rewriting the stored value when that field is left unchanged. Choosing a different integer saves that many whole minutes. The chart uses the displayed minutes; a preserved legacy sub-minute remainder can cause a small difference in the actual timing.

Shared progress is independent of the brightness range: temperature still changes when minimum and maximum brightness are equal. Color calibration and the separate brightness/color switches continue to apply. Explicit sleep mode always uses its own configured values. While shared temperature timing is enabled, it replaces the independent solar color curve, including `adapt_until_sleep` color blending before sleep mode activates.

### Natural

Keeps brightness at its maximum during daylight, with gradual changes at night. Temperature retains its independent solar curve. The two transition-window settings do not affect this mode.

### Linear

Changes the target at a constant rate. The nighttime window covers before sunrise and after sunset; the daytime window covers after sunrise and before sunset. Each full transition lasts the sum of the two windows. For example, 166 nighttime minutes and 1 daytime minute produce a 167-minute ramp, from 166 minutes before sunrise to 1 minute after, with the reverse timing around sunset. Events include configured times, bounds and offsets.

### Sigmoid

Uses an S-shaped curve: slower near the ends and faster in the middle. The same windows delimit approximately 5–95% of the change, with gentle tails outside them.

For either Linear or Sigmoid, setting **both windows to zero** selects a step: the target is at its maximum from sunrise (inclusive) until sunset, and at its minimum from sunset (inclusive) until sunrise. Setting just one window to zero keeps the transition on the other side of each event. The adaptation interval determines when commands are sent; the configured device transition can smooth them if the light supports it. These window settings do not replace that transition. No existing profile values are changed by the update.

## Available services

Circadian Pro provides the following Home Assistant services:

```text
circadian_pro.apply
circadian_pro.set_manual_control
circadian_pro.change_switch_settings
```

These services can be used from automations, scripts and Developer Tools.

## Release 0.21.4

- Fixed split brightness/color commands, manual-control detection and per-light service targeting, while preserving Home Assistant permissions.
- Hardened calibration preview ownership, cancellation, timeouts and restoration, including concurrent editors and delayed device responses.
- Improved configuration validation, lifecycle cleanup, YAML handling, translated selectors and wizard recovery after connection failures.
- Reduced repeated solar calculations and added polar-day/night handling compatible with Python 3.12 and 3.14.
- Completed the Circadian Pro branding review and included inherited-code license notices in the installation package.

Validation: 222 Python and 73 frontend tests, GitHub Actions on Python 3.12/3.14, and a live update from 0.21.3 to 0.21.4 on Home Assistant 2026.10.1. All three existing profiles, their configuration and 12 switch states were preserved. The wizard was checked without enabling previews; physical color output was not retested for this release.

## Release 0.21.3

- Corrected RGB+CCT adaptation using separate cold-white and warm-white channels, while retaining RGB, RGBW and native color-temperature support.
- Added physical white-channel settings and 4000 K / 1000 K calibration with immediate, optional light previews and automatic restoration.
- Added an automatic administrator sidebar panel for profile creation, configuration and calibration.
- Added compact light selection, wizard navigation, live profile updates and responsive mobile controls.
- Fixed calibration callbacks and WebSocket reconnection handling.
- Versioned panel scripts and custom elements by their contents to prevent stale interfaces after updates, including in the iOS Companion app.

Validated with 86 Python tests and 49 frontend tests, plus live Home Assistant and mobile checks.

## Release 0.20.3

* Updated config-entry lifecycle handling.
* Fixed mixed `light.toggle` behaviour.
* Improved cleanup of listeners, tasks and timers.
* Fixed stale light references after reloads.
* Improved manual-control reset handling.
* Added configuration validation and decimal-transition support.
* Fixed automatic sleep-mode state reporting.
* General code and translation cleanup.

## Important

Circadian Pro is a custom integration and is not part of the official Home Assistant project.

Compatibility can vary depending on the capabilities and implementation of each light integration.

## License and third-party notices

Original Circadian Pro source code and modifications are licensed under the [GNU GPLv3](LICENSE) (`GPL-3.0-only`). Commercial use and charging for distribution are allowed. Distributing a covered modified version requires compliance with GPLv3, including making its corresponding source available under the same license. Keeping private modifications does not require publishing them.

Inherited portions retain their Apache 2.0 license and attribution; the combined integration is distributed under GPLv3 with those notices preserved. Artwork and branding are outside the scope of this source-code licensing statement; no trademark rights are granted.

The integration, panel, entities and services use the Circadian Pro name and `circadian_pro` domain. Technical references to Home Assistant, WLED and other supported integrations describe compatibility.

Licensing and provenance for inherited code are recorded in [NOTICE](custom_components/circadian_pro/NOTICE) and the accompanying license files. Keep these files with copies of the integration, including installation ZIPs.

## Development checks

The [earlier audit report](docs/auditoria-2026-10-13.md) records that review's findings and validation limits.

Use Python 3.12 or newer and Node.js 24.22.1 (the version pinned in CI). The checks do not require a Home Assistant installation:

```sh
python -m pip install -r requirements-dev.txt
python scripts/check_sources.py
ruff check custom_components scripts --select E9,F,B
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.mjs
```

GitHub Actions runs the same checks on Python 3.12 and 3.14 for pushes and pull requests. HACS and Hassfest workflows separately check distribution metadata and Home Assistant integration structure. The regression tests execute production logic with Home Assistant I/O doubles; they complement live validation and do not replace testing with real light integrations.

Follow the [release procedure](docs/releasing.md) to keep the installed version, GitHub `main`, version tag and downloadable ZIP aligned after each completed update.

