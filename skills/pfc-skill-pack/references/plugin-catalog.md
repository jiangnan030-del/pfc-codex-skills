# Plugin Catalog

This catalog groups the 17 observed plugin folders by migration class.

## Geometry import
- `1等值线提取read_polyline_in_autocad`
- `2通过cad建立的wall导入pfc3D,cad_to_PFC3D.exe`
- `3.二维有限元网格生成pfc2d填充模型cad_to_pfc2d`
- `13.基于有限元网格用后退填充法生成pfc2d模型 finite_to_pfc2d_back_method`
- `14.基于三维有限元网格的颗粒填充程序 finite_to_pfc3d`

## Particle filling and grading
- `4.分级配颗粒流模型生成器cad_to_pfc2d_jipei`
- `9.二维填充法生成pfc2d模型delaunay_2d_shichong`
- `10.基于运动学的圆盘刚性簇细观模型构建程序fill_overlapping_disks`
- `11三维颗粒可重叠填充 Fill_3d_particle_by_overlapping_spheres`
- `12.finite_to_pfc2d`
- `17.抛石体填充颗粒流模型`

## Checking, grouping, and boundary utilities
- `5.复杂pfc2d模型材料分组设置`
- `6.有限元模型边界搜索程序_total boundary_search_3D`
- `7.有限元模型边界搜索程序_local boundray_search_3D_local`
- `8.有限元模型检查程序_2d boundary_search_2D`
- `15.施加滑面水压力_pfc3d`
- `16.matlab数字图像识别`

## Minimum note each migrated skill should preserve
- original folder name
- expected input file types
- expected output file types
- how the outputs feed a PFC6.0 `.dat` stage
- whether the old executable remains optional or is fully replaced
