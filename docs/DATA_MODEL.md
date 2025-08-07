
# Input List Data Model

This document outlines the hierarchical data model for the Input List project. The goal is to create a flexible, powerful, and open standard for describing the technical requirements of a musical performance.

The model is inspired by professional music software like Dorico, where data is structured logically in a hierarchy, and different "views" (like a stage plot or an input list) are derived from this central source of truth.

## Core Concepts

The data model is built around a few key entities:

-   **Band**: The root object representing a musical group. It contains all the other entities.
-   **Person**: A person, who can be a player or a contact.
-   **Player**: A musician in the band, linked to a `Person`.
-   **Instrument**: A physical item a player uses (e.g., a guitar, a keyboard).
-   **Input**: A single audio connection to the sound system.
-   **Channel**: A channel on the mixing console that an `Input` is patched to.
-   **Output**: A monitor speaker or in-ear monitor system.
-   **MonitorMix**: A description of what a player wants to hear in their monitor.
-   **Gear**: A specific piece of equipment (e.g., a Fender Twin Reverb amp, a Shure SM58 microphone).
-   **GearPreference**: A prioritized list for requesting gear, allowing for preferred, allowed, and disallowed options.

## The Hierarchy

-   A `Band` has many `Players`, `Instruments`, `Inputs`, `Channels`, and `Outputs`.
-   A `Player` is a `Person` and has many `Instruments` and `Outputs`.
-   An `Instrument` can generate many `Inputs`.
-   An `Input` is assigned to a `Channel`. Inputs can be linked (e.g., for stereo pairs).
-   A `MonitorMix` links a `Player` to a set of `Inputs`.

## Advanced Features

### Gear Requests (The "CSS Fonts" Rule)

To handle specific technical requirements professionally, we use a `GearPreference` model for both backline and microphone/DI requests. This allows artists to specify their needs with a clear order of preference, just like CSS `font-family` rules.

For example, when requesting a guitar amplifier, a musician can specify:
-   **Preferred**: A "Fender '65 Deluxe Reverb"
-   **Allowed**: A "Fender '65 Twin Reverb" or a "Vox AC30"
-   **Disallowed**: A "Marshall JCM800"

This is handled by referencing the `gear-preference-1.0.0.json` schema from within the `instrument` and `input` schemas. The `Gear` schema itself (`gear-1.0.0.json`) contains detailed fields for brand, model, version, power requirements, and connectors (XLR, TRS, etc.), making the requests unambiguous.

## Schemas

The data model is formally defined using JSON Schemas. The main schemas are:

-   `band-1.0.0.json`
-   `person-1.0.0.json`
-   `player-1.0.0.json`
-   `instrument-1.0.0.json`
-   `input-1.0.0.json`
-   `channel-1.0.0.json`
-   `output-1.0.0.json`
-   `monitormix-1.0.0.json`
-   `gear-1.0.0.json`
-   `gear-preference-1.0.0.json`

The existing `stage-plot-1.0.0.json` schema is now considered a "view" of this data model, and can be generated from the `Band` object.
