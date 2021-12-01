from pyecharts import Map, Geo
'''
    生成地图工具包
    需要安装依赖：
    pip install pyecharts
    pyecharts-snapshot
    pip install echarts-countries-pypkg
    pip install echarts-china-provinces-pypkg
    pip install echarts-china-cities-pypkg
    pip install echarts-china-counties-pypkg
    pip install echarts-china-misc-pypkg
'''

def get_single_product_province_map(map_name:str,data:dict,product_name:str,output_path:str = None,min_range:int = None,max_range:int = None):
    '''
        根据数据生成省份分布图
        map_name:str
            地图名称，如：九阳全国销售分布图
        data:dict
            数据，字典类型，传入格式：{'北京':12,'河北':33,...} 标准省份名称+数值
        product_name:str
            产品名称：九阳豆浆机...
        output_path:str
            输出文件名称，输出文件为html，文件路径以.html结尾，默认为.../render.html 如: /jiuyang_product.html
        range_min:int
            分布range最小值，默认为传入数据最小值，否则为传入数值
        range_max:int
            分布range最大值，默认为传入数据最大值，否则为传入数值
    '''
    attr = data.keys()
    value = data.values()
    range_min = min_range if min_range is not None else min(value)
    range_max = max_range if max_range is not None else max(value)
    visual_range = [range_min,range_max]
    map = Map(map_name, width=1200, height=600)
    map.add(
        product_name,
        attr,
        value,
        maptype="china",
        visual_range=visual_range,
        is_visualmap=True,
        is_label_show=True,
        visual_text_color="#000",
    )
    if output_path:
        map.render(output_path)
    else:
        map.render()

def get_multi_product_province_map(map_name:str,datas,product_names,output_path:str = None,min_range:int = None,max_range:int = None):
    '''
        根据多组数据生成多个系列省份分布图
        map_name:str
            地图名称，如：九阳全国销售分布图
        datas: list(dict)
            数据，字典数组，传入格式：[{'北京':12,'河北':33,...},...] 标准省份名称+数值
        product_names: list(str)
            产品名称数组，需要和字典列表一一对应：[九阳豆浆机,...]...
        output_path:str
            输出文件名称，输出文件为html，文件路径以.html结尾，默认为.../render.html 如: /jiuyang_product.html
        range_min:int
            分布range最小值，默认为传入数据最小值，否则为传入数值
        range_max:int
            分布range最大值，默认为传入数据最大值，否则为传入数值
    '''
    map = Map(map_name, width=1200, height=600)
    min_mounts = [min(data.values()) for data in datas]
    max_mounts = [max(data.values()) for data in datas]
    range_min = min_range if min_range is not None else min(min_mounts)
    range_max = max_range if max_range is not None else max(max_mounts)
    visual_range = [range_min,range_max]
    for index, item in enumerate(product_names):
        data = datas[index]
        product_name = item
        attr = data.keys()
        value = data.values()
        map.add(
            product_name,
            attr,
            value,
            maptype="china",
            visual_range=visual_range,
            is_visualmap=True,
            is_label_show=True,
            visual_text_color="#000",
        )
    if output_path:
        map.render(output_path)
    else:
        map.render()

def get_single_product_city_map(map_name:str,data:dict,product_name:str,output_path:str = None,min_range:int = None,max_range:int = None):
    '''
        根据数据生成城市分布图
        map_name:str
            地图名称，如：九阳全国销售分布图
        data:dict
            数据，字典类型，传入格式：{'信阳':12,'杭州':33,...} 标准省份名称+数值
        product_name:str
            产品名称：九阳豆浆机...
        output_path:str
            输出文件名称，输出文件为html，文件路径以.html结尾，默认为.../render.html 如: /jiuyang_product.html
        range_min:int
            分布range最小值，默认为传入数据最小值，否则为传入数值
        range_max:int
            分布range最大值，默认为传入数据最大值，否则为传入数值
    '''
    source = [(key,value) for key,value in data.items()]
    range_min = min_range if min_range is not None else min(value)
    range_max = max_range if max_range is not None else max(value)
    visual_range = [range_min,range_max]
    geo = Geo(
        map_name,
        "",
        title_color="#fff",
        title_pos="left",
        width=1200,
        height=600,
        background_color="#404a59",
    )
    attr, value = geo.cast(source)
    geo.add(product_name, attr, value, type="effectScatter",visual_range=visual_range, is_random=True, effect_scale=5)
    if output_path:
        geo.render(output_path)
    else:
        geo.render()


def get_multi_product_city_map(map_name:str,datas,product_names,output_path:str = None,min_range:int = None,max_range:int = None):
    '''
        根据多组数据生成多个系列城市分布图
        map_name:str
            地图名称，如：九阳全国销售分布图
        datas: list(dict)
            数据，字典数组，传入格式：[{'北京':12,'河北':33,...},...] 标准省份名称+数值
        product_names: list(str)
            产品名称数组，需要和字典列表一一对应：[九阳豆浆机,...]...
        output_path:str
            输出文件名称，输出文件为html，文件路径以.html结尾，默认为.../render.html 如: /jiuyang_product.html
        range_min:int
            分布range最小值，默认为传入数据最小值，否则为传入数值
        range_max:int
            分布range最大值，默认为传入数据最大值，否则为传入数值
    '''
    geo = Geo(
        map_name,
        "",
        title_color="#fff",
        title_pos="left",
        width=1200,
        height=600,
        background_color="#404a59",
    )
    min_mounts = [min(data.values()) for data in datas]
    max_mounts = [max(data.values()) for data in datas]
    range_min = min_range if min_range is not None else min(min_mounts)
    range_max = max_range if max_range is not None else max(max_mounts)
    visual_range = [range_min,range_max]
    for index, item in enumerate(product_names):
        data = datas[index]
        product_name = item
        source = [(key,value) for key,value in data.items()]
        attr, value = geo.cast(source)
        geo.add(product_name, attr, value, type="effectScatter", visual_range=visual_range, is_random=True, effect_scale=5)
    if output_path:
        geo.render(output_path)
    else:
        geo.render()
 
get_multi_product_province_map('九阳全国销量图',[{'河北':10,'河南':200,'浙江':1000},{'西安':2000,'四川':20,'安徽':200}],['九阳豆浆机','抽油烟机'],max_range=1500,min_range=15)