import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { motion } from "framer-motion"

const topics = [
  { id: 1, title: "Excel cơ bản" },
  { id: 2, title: "Excel nâng cao" },
  { id: 3, title: "Phân tích dữ liệu" },
  { id: 4, title: "Hàm Excel chuyên sâu" },
  { id: 5, title: "Excel cho kế toán" },
  { id: 6, title: "Thống kê bằng Excel" },
]

export default function TopicSelect() {
  return (
    <div className="min-h-screen bg-[#f5f6fa] flex flex-col items-center py-12 px-4">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-4xl font-bold text-gray-800 mb-4"
      >
        Quiz App
      </motion.h1>

      <motion.h2
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="text-2xl font-semibold text-gray-600 mb-10"
      >
        Chọn Chủ Đề
      </motion.h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl">
        {topics.map((topic, index) => (
          <motion.div
            key={topic.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 * index }}
          >
            <Card className="p-6 rounded-2xl shadow-md bg-white text-center hover:shadow-lg transition-all">
              <CardContent>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">{topic.title}</h3>
                <Button className="bg-purple-600 text-white hover:bg-purple-700 shadow">Bắt đầu</Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <footer className="mt-12 text-sm text-gray-400">© 2025 Quiz App. All rights reserved.</footer>
    </div>
  )
}
