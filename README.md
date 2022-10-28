# python程设



#### **模块介绍**

##### car_url_get.py

功能介绍提取页面URL,保存至url.txt文件中

<img src="C:\Users\旧多\AppData\Roaming\Typora\typora-user-images\image-20221028124850562.png" alt="image-20221028124850562" style="zoom:50%;" />



##### car_spider.py

```
 spider(url)
```

将下图URL保存至big_url_2中

<img src="C:\Users\旧多\AppData\Roaming\Typora\typora-user-images\image-20221028125456233.png" alt="image-20221028125456233" style="zoom:50%;" />

将在售，停售，即将销售的URL保存至sort_name_3中

<img src="C:\Users\旧多\AppData\Roaming\Typora\typora-user-images\image-20221028125738021.png" alt="image-20221028125738021" style="zoom:50%;" />

根据在售，停售，即将销售判断使用

1. ```
   current_spider(url)
   ```
   获得品牌，车系，用户评分，经销商价格，售价，用户评价

2. ```
   future_spider(url)
   ```
   获得品牌，车系，用户评分，经销商价格，售价，用户评价

3. ```
   stop_spider(url)
   ```
   获得品牌，车系，用户评分，经销商价格，售价，用户评价

```
get_car_list(url)
```
获取车辆id存在car_list中

<img src="C:\Users\旧多\AppData\Roaming\Typora\typora-user-images\image-20221028130533048.png" alt="image-20221028130533048" style="zoom:50%;" />

```
deliver_current_change(content)
deliver_future_change(content)
```
根据一个网络请求相信获得经销商报价

```
koubei(car_id)
```

根据car_id进入URL('https://k.autohome.com.cn/' + str(car_id))获得用户评价并拼接成字典格式

![image-20221028131736191](C:\Users\旧多\AppData\Roaming\Typora\typora-user-images\image-20221028131736191.png)
