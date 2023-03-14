#!/usr/bin/env python
import io
import unittest
from extra.utils import fetch, fake_torch_load_zipped
from PIL import Image

class TestUtils(unittest.TestCase):  
  def test_fetch_bad_http(self):
    self.assertRaises(AssertionError, fetch, 'http://httpstat.us/500')
    self.assertRaises(AssertionError, fetch, 'http://httpstat.us/404')
    self.assertRaises(AssertionError, fetch, 'http://httpstat.us/400')
  
  def test_fetch_small(self):
    assert(len(fetch('https://google.com'))>0)

  def test_fetch_img(self):
    img = fetch("https://media.istockphoto.com/photos/hen-picture-id831791190")
    pimg = Image.open(io.BytesIO(img))
    assert pimg.size == (705, 1024)

  def test_fake_torch_load_zipped(self):
    import torch
    import numpy as np
    import tempfile
    class LayerWithOffset(torch.nn.Module):
      def __init__(self):
        super(LayerWithOffset, self).__init__()
        self.param = torch.nn.Parameter(
          torch.randn(16).as_strided([4], [1], storage_offset=5)
        )

    for isfloat16 in [True, False]:
      model = torch.nn.Sequential(
        torch.nn.Linear(4, 8),
        torch.nn.Linear(8, 3),
        LayerWithOffset()
      )
      if isfloat16: model = model.half()

      with tempfile.TemporaryDirectory() as tmpdirname:
        path = tmpdirname + '/testloadmodel.pth'
        torch.save(model.state_dict(), path)
        model2 = fake_torch_load_zipped(path)

      for name, a in model.state_dict().items():
        b = model2[name]
        a, b = a.numpy(), b.numpy()
        assert a.shape == b.shape
        assert a.dtype == b.dtype
        assert np.array_equal(a, b)


if __name__ == '__main__':
  unittest.main()