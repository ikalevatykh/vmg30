# vmg30
Client for VMG30 glove from Virtual Motion Lab.

## Install

### From source code

```
git clone https://github.com/ikalevatykh/vmg30.git
cd vmg30
python setup.py install
```

## Examples

### An example of usage

```python
from vmg30.glove import Glove
from vmg30.model import HandModel

model = HandModel()

with Glove(port='/dev/ttyUSB0') as glove:
    print(f'Glove id: {glove.device_id}')
    with glove.sampling():
        for i in range(10):
            sample = glove.next_sample()
            print('Glove raw sample:')
            print(sample)
            points = model.points(sample)
            print('Skeleton points:')
            for link, point in points.items():
                print(f'- {link}: {point}')
```

### Visualise the hand skeleton

![Hand skeleton](https://github.com/ikalevatykh/vmg30/blob/master/images/hand_anim.gif?raw=true "Hand skeleton")

You need to install [panda3d_viewer](https://github.com/ikalevatykh/panda3d_viewer/) to use visualiser:

```
pip install panda3d_viewer
```


```python
from panda3d_viewer import Viewer, ViewerConfig

from vmg30.glove import Glove
from vmg30.view import HandView

config = ViewerConfig(scene_scale=10.0, show_grid=False)

with Viewer(window_title='VMG30', config=config) as viewer:
    viewer.reset_camera(pos=(5, 5, 5), look_at=(0, 0, 0))
    hand_view = HandView(viewer)

    with Glove('/dev/ttyUSB0') as glove:
        with glove.sampling():
            while True:
                hand_view.update(glove.next_sample())
```

## Tools

- `python -m vmg30.tools.info --port {port}` - show information about of the glove, connected to the `{port}`.
- `python -m vmg30.tools.dump --port {port} --file {pickle_file}` - record samples from the glove to an output pickle file.
- `python -m vmg30.tools.show --port {port}` - visualise the hand skeleton using a real time  glove samples.
- `python -m vmg30.tools.show --file {pickle_file}` - visualise the hand skeleton using a prerecorded glove samples.


## License

*vmg30* is licensed under the MIT License - see the LICENSE file for details.