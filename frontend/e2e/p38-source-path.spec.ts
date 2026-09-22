import { expect, test } from '@playwright/test'

/**
 * S-2 关闭证据：P38「产品解读与知识」页不得暴露服务器绝对路径。
 *
 * 依据：Owner 2026-09-22 授权（范围仅限删除前端绝对路径拼接 + 同步本断言）。
 * 修复前：页面"产品原始文件"渲染 `/home/szf/dev/Leibniz-KERT/.../PROD-*.md`（R2 `07` §3 已留证）。
 * 修复后：仅渲染相对 `sourceFile`（如 `cash-management/version=…/product-cards/PROD-CM-003.md`）。
 */
const FORBIDDEN = ['/home/', '/Users/', 'Leibniz-KERT', 'gits-cbanking']

test.describe('P38 源文件路径收口（S-2）', () => {
  test('页面文本不得出现服务器绝对路径；相对标识必须可见', async ({ page }) => {
    await page.setViewportSize({ width: 1608, height: 932 })
    await page.goto('/product-knowledge/interpretation', { waitUntil: 'networkidle' })
    await page.waitForSelector('[data-testid="p38-product-interpretation"]', { timeout: 20000 })

    // 选中一个产品，触发摘要卡渲染（含"产品原始文件"）
    const first = page.locator('.n-list-item').first()
    await first.click()
    await page.waitForTimeout(1200)

    const body = await page.locator('body').innerText()
    for (const token of FORBIDDEN) {
      expect(body, `页面文本不得包含 ${token}`).not.toContain(token)
    }

    // 相对源文件标识应可见（形如 .../product-cards/PROD-*.md）
    const srcPath = page.locator('.src-path').first()
    await expect(srcPath).toBeVisible()
    await expect(srcPath).toContainText('product-cards/PROD-')
    expect((await srcPath.innerText()).startsWith('/')).toBe(false)
  })
})
