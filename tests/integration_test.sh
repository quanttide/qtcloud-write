#!/usr/bin/env bash
API="http://localhost:8000"
PASS=0
FAIL=0

ok()   { echo "  PASS"; PASS=$((PASS+1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

summary() { echo ""
echo "=== 结果: $PASS 通过, $FAIL 失败 ==="; exit $FAIL; }

echo "=== 前后端联调: 写作云 Provider ↔ Flutter Client ==="

# 1. 服务可达
echo "1) 服务可达"
code=$(curl -s -o /dev/null -w "%{http_code}" "$API/docs")
[ "$code" = "200" ] && ok || fail "GET /docs = $code"

# 2. 提交好文章 → 风格积累
echo "2) 提交好文章（风格积累）"
GOOD_RESP=$(curl -s -X POST "$API/review" \
  -H "Content-Type: application/json" \
  -d @/tmp/opencode/good_article.json)
echo "  摘要: $(echo "$GOOD_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['summary'])")"

# 3. Flutter Review.fromJson 字段校验
echo "3) Flutter 字段映射校验"
python3 -c "
import json, sys
d = json.load(sys.stdin)
for f in ['article_title','author','tag','summary','paragraphs','is_style_available','suggestions']:
    assert f in d, f'缺少 {f}'
for p in d['paragraphs']:
    for f in ['original','analysis','tag','comparison']:
        assert f in p, f'段落缺少 {f}'
    if p['comparison']:
        for f in ['type','issue','demo']:
            assert f in p['comparison'], f'comparison 缺少 {f}'
print('  所有字段匹配 ✓')
" <<< "$GOOD_RESP" && ok || fail "字段校验失败"

# 4. CORS 头
echo "4) CORS 头"
cors=$(curl -s -D- -X OPTIONS "$API/review" \
  -H "Origin: http://localhost:4200" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  2>/dev/null | grep -i "access-control-allow-origin" | tr -d '\r\n')
echo "  $cors"
[ -n "$cors" ] && ok || fail "CORS 头缺失"

# 5. 提交坏文章 → 风格对比
echo "5) 提交坏文章（风格对比）"
BAD_RESP=$(curl -s -X POST "$API/review" \
  -H "Content-Type: application/json" \
  -d @/tmp/opencode/bad_article.json)
python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['is_style_available'] == True, '风格不可用'
assert len(d['suggestions']) > 0, '无建议'
bad = sum(1 for p in d['paragraphs'] if p.get('comparison') and p['comparison']['type'] == 'bad')
print(f'  建议: {len(d[\"suggestions\"])} 条')
print(f'  坏对比段落: {bad} 段')
assert bad > 0, '无坏对比'
print('  对比结果正确 ✓')
" <<< "$BAD_RESP" && ok || fail "坏文章对比失败"

# 6. 422 验证错误处理
echo "6) 422 错误处理"
err_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API/review" \
  -H "Content-Type: application/json" \
  -d '{"title":"only title"}')
[ "$err_code" = "422" ] && ok || fail "期望 422 实际 $err_code"

summary
