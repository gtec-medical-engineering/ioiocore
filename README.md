# ioiocore

[![PyPI version](https://img.shields.io/pypi/v/ioiocore.svg)](https://pypi.org/project/ioiocore/)
[![License](https://img.shields.io/badge/license-GNCL-blue)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-green)](https://gtec-medical-engineering.github.io/ioiocore/)
[![Build Status](https://github.com/gtec-medical-engineering/ioiocore-dev/actions/workflows/ci.yml/badge.svg)](https://github.com/gtec-medical-engineering/ioiocore-dev/actions)

**A real-time data processing framework for Python.**

`ioiocore` is a high-performance framework for processing real-time EEG and BCI signals. It provides a modular architecture for signal acquisition, processing, and visualization.

## Features
- Modular design – Build custom signal processing pipelines
- Real-time performance – Optimized for low-latency processing
- Device integration – Compatible with multiple EEG hardware devices
- WebSocket-based communication – Easily interface with external applications
- Extensible API – Develop custom processing nodes

## Installation
`ioiocore` is available on PyPI:

```
pip install ioiocore
```

To use the latest development version:

```
pip install git+https://github.com/gtec-medical-engineering/ioiocore-dev.git
```

## Quick Start
```python
import ioiocore

# Initialize a processing pipeline
pipeline = ioiocore.Pipeline()

# Add a processing node (e.g., a bandpass filter)
pipeline.add_node(ioiocore.nodes.Filter(low=1.0, high=30.0))

# Start processing
pipeline.run()
```

## Documentation
Full documentation is available at [GitHub Pages](https://gtec-medical-engineering.github.io/ioiocore/).

## License
This project is licensed under the **G.tec Non-Commercial License (GNCL)**. See the [LICENSE](LICENSE) file for details.

## Contributing
We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support
For support, please contact [support@gtec.at](mailto:support@gtec.at).
