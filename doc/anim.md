`TimedAnimation` 的子类，通过重复调用函数 *func* 来制作动画。

.. 注意::

    必须将创建的 Animation 存储在一个变量中，并确保该变量的生命周期与动画运行时间一致。
    否则，Animation 对象会被垃圾回收，动画将停止。

参数
----------
fig : `~matplotlib.figure.Figure`
    用于获取所需事件（如绘制或调整大小）的图形对象。

func : callable
    每帧调用的函数。第一个参数将是 *frames* 中的下一个值。
    可以使用 `functools.partial` 或通过 *fargs* 参数提供额外的位置参数。

    函数的必需签名为::
    
        def func(frame, *fargs) -> iterable_of_artists
    
    通常使用 `functools.partial` 提供参数更为方便。
    通过这种方式，还可以传递关键字参数。
    如果需要传递同时包含位置参数和关键字参数的函数，可以将所有参数设置为关键字参数，仅保留 *frame* 参数未设置::
    
        def func(frame, art, *, y=None):
            ...
    
        ani = FuncAnimation(fig, partial(func, art=ln, y='foo'))
    
    如果 ``blit == True``，*func* 必须返回一个包含所有被修改或创建的艺术家对象的可迭代对象。
    这些信息将被 blitting 算法用来确定需要更新的图形部分。
    如果 ``blit == False``，返回值将被忽略，此时可以省略返回值。

frames : iterable, int, generator function, or None, optional
    用于传递给 *func* 和动画每帧的数据源。

    - 如果是可迭代对象，则直接使用提供的值。如果可迭代对象有长度，将覆盖 *save_count* 参数。
    - 如果是整数，则等同于传递 ``range(frames)``。
    - 如果是生成器函数，则必须具有以下签名::
    
         def gen_function() -> obj
    
    - 如果为 *None*，则等同于传递 ``itertools.count``。
    
    在所有这些情况下，*frames* 中的值将直接传递给用户提供的 *func*，因此可以是任何类型。

init_func : callable, optional
    用于绘制清晰帧的函数。如果未提供，将使用从帧序列的第一个项目绘制的结果。
    此函数将在第一帧之前调用一次。

    函数的必需签名为::
    
        def init_func() -> iterable_of_artists
    
    如果 ``blit == True``，*init_func* 必须返回一个包含需要重新绘制的艺术家对象的可迭代对象。
    这些信息将被 blitting 算法用来确定需要更新的图形部分。
    如果 ``blit == False``，返回值将被忽略，此时可以省略返回值。

fargs : tuple or None, optional
    传递给每次调用 *func* 的额外参数。注意：推荐使用 `functools.partial` 而不是 *fargs*。
    详情请参阅 *func*。

save_count : int, optional
    用于缓存 *frames* 中值的数量的回退值。
    仅当无法从 *frames* 推断帧数时（例如，当 *frames* 是无长度的迭代器或生成器时）使用。

interval : int, default: 200
    帧之间的延迟（以毫秒为单位）。

repeat_delay : int, default: 0
    如果 *repeat* 为 True，则为连续动画运行之间的延迟（以毫秒为单位）。

repeat : bool, default: True
    当帧序列完成时，动画是否重复。

blit : bool, default: False
    是否使用 blitting 优化绘图。
    注意：使用 blitting 时，任何动画艺术家将根据其 zorder 绘制；
    然而，它们将绘制在任何先前艺术家的顶部，而不管其 zorder。

cache_frame_data : bool, default: True
    是否缓存帧数据。如果帧包含大型对象，禁用缓存可能会有所帮助。