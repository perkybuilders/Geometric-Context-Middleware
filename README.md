# Geometric Context Middleware (GCM)

## Project Vision

Modern Large Language Models (LLMs) suffer from a critical vulnerability: the "Forgetful AI" problem. As conversations lengthen or tasks become complex, models lose context, hallucinate facts, and drift from the original goal.

The Geometric Context Middleware (GCM) is a "Sober AI" architecture engineered to solve this. By mapping thoughts, states, and logic in a deterministic 3D Euclidean Vector Space, GCM provides a rigid structural backbone for LLMs. Instead of relying purely on token-based attention mechanisms that degrade over time, GCM grounds the AI's reasoning within spatial constraints, preventing context loss and hallucination through mathematical grounding.

## The 3D Coordinate Map

The core of GCM is its spatial memory mapping system. Every context node (a "thought" or "state") is anchored in a 3D coordinate space ($X, Y, Z$).

*   **$X$ (Timeline): `0` (Start) to `100` (End)**
    *   Represents chronological or logical progression. It enforces sequential reasoning.
*   **$Y$ (Resolution): `0` (Big Vision) to `100` (Hard Code)**
    *   Represents the level of abstraction. A low $Y$ signifies high-level architecture or strategy, while a high $Y$ dictates low-level implementation details.
*   **$Z$ (Aesthetic): `0` (Logic) to `100` (Persona/Vibe)**
    *   Governs the tone, strictness, and style of the output. Near `0` represents strict deterministic output, while closer to `100` allows for conversational tone and creative extrapolation.

## The Three Guardians (The Code Architecture)

GCM is governed by three primary, interlocking systems designed to maintain the integrity of the Context Graph:

1.  **`registry.py` (The Memory)**
    *   Responsible for the persistence layer. It manages atomic data saves and loads via `geometric_registry.json`. It guarantees state retention across sessions.
2.  **`orchestrator.py` (The GPS)**
    *   Calculates Euclidean distances to find nearest neighbor nodes and builds the active Context Harness. It ensures the LLM is always fed the geometrically most relevant context.
3.  **`observer.py` (The Teacher)**
    *   Monitors LLM outputs for deviations from the established graph. If the AI hallucinates or drops context, the Observer triggers "Re-Grounding Maneuvers," generating bridge dots to resolve 'Voids' (unlinked nodes) and mathematically pulling the LLM back to reality.

## Feature Set (v1.5)

GCM includes advanced graph dynamics to simulate human-like attention and memory retention:

*   **Temporal Decay:** Nodes in the Geometric Context Graph have dynamic weights governed by a Pulse Engine. Entropy Decay reduces weights gradually (by 5%, down to a floor of 1.0) on initialization and listing, mimicking the natural fading of old information.
*   **Resonance (Heat):** When nodes are intercepted by the Orchestrator and used as reference dots (or linked via Re-Grounding), their weights gain "Resonance Heat" (boosted by 1.0, up to a max of 10.0). This is visualized via a Heat Bar in the CLI, ensuring frequently accessed context remains top-of-mind.

## Getting Started (The Implementation Loop)

To run the interactive CLI and interact with the 3D map, execute:
```bash
python cli.py
```

Inside the CLI, you can manage the graph via the following commands:

*   **Planting the seed:**
    ```bash
    add <content> [x y z]
    # Example: add "Initialize core logic" 10 90 10
    ```
*   **Moving focus:**
    ```bash
    shift <axis> <value>
    # Example: shift x 80
    ```
*   **Welding connections:**
    ```bash
    link <source_prefix> <target_prefix> [rel_type]
    # Example: link 8a1b 9c2d EXPANSION
    ```
*   **Testing the logic:**
    ```bash
    simulate <response>
    # Example: simulate "The code is written, shifting to next phase."
    ```

## Testing Capabilities

The project enforces robust unit testing to maintain the reliability of the middleware. To verify the system's integrity, use the standard unittest suite:

```bash
python -m unittest discover tests
```

The test suite continuously verifies:
*   **Persistence:** Confirming that the JSON registry accurately saves, locks, and swaps files without data corruption.
*   **Sobriety:** Ensuring the Observer correctly detects hallucinations, flags voids, and triggers Re-Grounding Maneuvers accurately.
*   **Heat Decay:** Validating the mathematics behind Temporal Decay and Resonance, checking that weights pulse correctly over time.
