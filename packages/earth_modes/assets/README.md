# Shared visual assets

`coastlines.json`: Natural Earth 1:110m coastline v4.1.0. Public domain. Coordinates are longitude, latitude in degrees; separate lines must not be joined. Original archive SHA-256 and source URL are in the JSON. Source: https://www.naturalearthdata.com/downloads/110m-physical-vectors/110m-coastline/ and https://www.naturalearthdata.com/about/terms-of-use/ . No network access is needed at runtime.

`palettes.json`: fixed 256-entry sRGB float triples. Signed data uses the original blue/neutral/amber palette; magnitude uses Matplotlib cividis. Both backends use floor(clamp(t,0,1)*255), where t=(value+limit)/(2*limit) for signed data and value/limit for magnitude. No automatic per-frame normalization. Matplotlib color data is distributed under its PSF-based license: https://matplotlib.org/stable/project/license.html .
