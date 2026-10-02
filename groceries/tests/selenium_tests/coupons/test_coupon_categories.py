from pages.LuckyCoupons import LuckyCouponsSelenium


def test_coupon_categories_showing_and_click_meat_seafood(
    luckyCouponsSelenium: LuckyCouponsSelenium,
):
    page = luckyCouponsSelenium

    page.goToCouponsLandingPage()

    categories = page.getCouponCategories()
    assert len(categories) > 0
    assert any(cat.text.strip() == "Meat & Seafood" for cat in categories)

    page.clickCouponCategory("Meat & Seafood")

    assert "meat-seafood" in page.driver.current_url