# images_cut_finished 文件说明

- 文件夹的名字代表各个原图片，由新上传的sheet_music_detailed.py生成，运行时注意修改路径

- 切割的逻辑分为三部：

   	1. line_cut: 将乐谱切分为单行
   	2. bar_cut: 将单行乐谱按小节切分
   	3. voice_part_cut: 将完成小节切分后的乐谱按声部切分(即最后的结果，放在每个源图片的result文件夹内)

- 具体解释

  ​    ![1549858467325](C:\Users\PKU\AppData\Roaming\Typora\typora-user-images\1549858467325.png)

  1. img_projection.png: 乐谱图向左投影后得到的图，左侧的阴影代表这一行像素值的多少
  2. bar_cut_i_j.png: i代表是由哪行乐谱切得的，即第几个line_cut图像得到的，j代表在这一行乐谱切分得到的第几小节, e.g. bar_cut_1_2代表由line_cut_1.png得到的第3小节(从0开始计数)
  3. result文件夹中的图片与2同理，voice_part_cut_i_j_k.png: i,j代表bar_cut_i_j.png得到的,k=0代表高声部(靠上的那行)，k=1代表低声部(靠下的那行)

  ![1549862248415](C:\Users\PKU\AppData\Roaming\Typora\typora-user-images\1549862248415.png)

