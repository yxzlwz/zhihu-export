// 本代码来自GPT-4o：https://chatgpt.com/share/5be5269e-cf5f-4755-ae72-135aea27ee12

const SleepSecond = 5;

async function scrapeZhihu() {
    // 用于存储结果的数组
    const results = [];

    // 递归函数，用于翻页和数据采集
    async function scrapePage() {
        // 获取答案链接
        const items = document.querySelectorAll(
            '.ContentItem-title > div[itemprop="zhihu:question"]'
        );
        items.forEach(item => {
            const name = item
                .querySelector('meta[itemprop="name"]')
                .getAttribute("content");

            const linkElement = item.querySelector(
                'a[target="_blank"][data-za-detail-view-element_name="Title"]'
            );
            if (linkElement) {
                const url = linkElement.getAttribute("href");
                // 确保链接是相对路径
                if (url.startsWith("//www.zhihu.com/question/")) {
                    results.push({ title: name, answer_url: "https:" + url });
                }
            }
        });

        // 查找下一页按钮
        const nextPageButton = document.querySelector(
            ".Button.PaginationButton.PaginationButton-next"
        );

        if (nextPageButton) {
            // 点击下一页按钮
            nextPageButton.click();
            console.log(`已点击下一页按钮，等待${SleepSecond}秒...`);
            // 等待5秒后继续采集数据
            await new Promise(resolve =>
                setTimeout(resolve, SleepSecond * 1000)
            );
            await scrapePage();
        } else {
            // 如果没有下一页按钮，结束采集
            console.log("到达最后一页，停止采集。");
            // 导出结果为JSON
            const json = JSON.stringify(results, null, 2);
            console.log("导出的JSON数据：", json);
            const blob = new Blob([json], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "zhihu_data.json";
            a.click();
        }
    }

    // 开始采集
    await scrapePage();
}

// 运行采集函数
scrapeZhihu();
