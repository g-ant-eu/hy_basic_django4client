
# A simple JWT and Whitenoise django integration module

## Usage

Inside settings.py:

```python
import hy_basic_django4client 
import sys
hy_basic_django4client.config.configure_django(sys.modules[__name__])
```

This enables the project to use JWT and Whitenoise.

