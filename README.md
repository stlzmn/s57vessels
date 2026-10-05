# s57vessels

Radar-style navigation simulator that displays own ship and surrounding vessel traffic over
S-57 electronic navigational chart data, with collision risk assessment.

## What it does

- Reads AIS/NMEA traffic over TCP and own-ship GPS data over serial, and tracks vessel state.
- Renders an ENC-style radar display (own ship, targets, range rings) with Pygame.
- Parses S-57 chart cells for the displayed area.
- Computes line-of-sight/collision geometry and vessel risk assessment (CPA/TCPA-style checks)
  in `collision_monitor.py`, with GPU-accelerated geometry via Numba.
- Runs closest-point-of-approach / maneuver trial calculations (`collzone_handler.py`,
  `collzone/`) in a separate worker process, backed by an MS SQL Server database via `pyodbc`.
  The actual calculation logic in `collzone/` is proprietary and has been stripped from this
  public copy (signatures only, function bodies removed).
- Includes an early-stage Gym environment (`s57ais_env.py`) for future reinforcement-learning
  experiments on top of the simulator.

## Project layout

- `source/entry_point.py` - application entry point
- `source/application.py`, `source/radar.py`, `source/display.py` - main app loop and radar display
- `source/dataflow.py`, `source/nmea_parser.py` - AIS/NMEA data ingestion
- `source/ship_handling.py`, `source/navi_calculator.py`, `source/geodesic_calc.py` - vessel state and navigation math
- `source/s57.py` - S-57 chart cell parsing
- `source/collision_monitor.py`, `source/collzone_handler.py`, `source/collzone/` - collision detection and risk assessment
- `source/user_interface.py`, `source/tkinter_dialogs.py` - UI panels and dialogs
- `assets/` - display assets (icons)

## Chart data

This repository does not ship S-57 ENC chart cells. Official ENC data (e.g. from a national
hydrographic office or a RENC/PRIMAR/IC-ENC distributor) is copyrighted and licensed, not
freely redistributable. Place your own licensed `.000` cells under a local `maps/` directory
(ignored by git) before running the app; see `source/init_params.py` for the expected
filenames/paths.

## Running

```bash
cd source
python entry_point.py
```

Requires a reachable AIS source, a GPS serial feed, licensed S-57 chart data under `maps/`,
and (for the COLLZONE risk-assessment worker) access to an MS SQL Server database via `pyodbc`.

## Testing

Unit tests cover the dependency-light modules (coordinate conversion, descriptor-based
models, navigation math) and skip modules that require heavy/native dependencies
(Pygame, GDAL, Numba) when those aren't installed.

```bash
pip install -r requirements.txt
pytest
```

## License

MIT - see [LICENSE](LICENSE). Keep the copyright notice and give credit if you reuse this code.
