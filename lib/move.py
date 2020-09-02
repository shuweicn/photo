# def move(p):
#     if p.src in photo_countinue:
#         p.status = 'continue'
#         return
#
#     may_pair = aae_pairs.get(p.src)
#     if may_pair:
#         pair = session.query(Photo).filter_by(src=may_pair).one()
#         dest = pair.dst.rsplit('.', 1)[0]
#         dest += '.AAE'
#         p.dst = dest
#     else:
#         dest = p.dst
#
#     print(p.src, dest)
#     base = path.dirname(p.dst)
#     if not os.path.exists(base):
#         os.makedirs(base)
#
#     try:
#         if os.path.exists(p.src) and not os.path.exists(p.dst):
#             shutil.move(p.src, p.dst)
#             p.status = 'dest'
#             pass
#         else:
#             print('error', os.path.exists(p.src), os.path.exists(p.dst))
#     except FileNotFoundError:
#         print('alreay_moved ', p.src)