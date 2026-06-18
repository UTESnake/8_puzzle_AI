# 8-Puzzle Search Algorithms

## 1. Giới thiệu đề tài

Dự án này mô phỏng bài toán **8-Puzzle** bằng Python và Pygame. Người dùng có thể di chuyển các ô số bằng phím mũi tên hoặc chọn thuật toán để chương trình tự tìm đường đi từ trạng thái ban đầu đến trạng thái đích.

Bài toán 8-Puzzle gồm một bảng 3x3 có 8 ô số và 1 ô trống. Mỗi bước đi là thao tác trượt một ô số vào vị trí ô trống. Mục tiêu là biến đổi trạng thái hiện tại về trạng thái mẫu với số bước hợp lệ.

Trong chương trình, trạng thái mặc định là:

```text
Trạng thái ban đầu:
0 6 5
2 1 8
7 4 3

Trạng thái đích:
1 2 3
4 5 6
7 8 0
```

Trong đó `0` biểu diễn ô trống.

---

## 2. Mục tiêu của chương trình

- Xây dựng giao diện trực quan cho bài toán 8-Puzzle.
- Cho phép người dùng chơi thủ công bằng phím mũi tên.
- Cài đặt nhiều nhóm thuật toán tìm kiếm khác nhau.
- Minh họa quá trình giải bằng animation từng bước.
- Ghi log số bước, hướng di chuyển và giá trị đánh giá như `g(n)`, `h(n)`, `f(n)`.
- So sánh hiệu quả giữa các thuật toán trong cùng nhóm và khác nhóm.

---

## 3. Công nghệ sử dụng

- Ngôn ngữ: **Python**
- Thư viện giao diện: **Pygame**
- Cấu trúc dữ liệu chính: `list`, `set`, `deque`, `heapq`, cây trạng thái thông qua lớp `Node`
- Heuristic chính: **Manhattan Distance**

---

## 4. Cấu trúc thư mục

```text
8_puzzle/
├── main.py
├── ui.py
├── grid.py
├── utils.py
├── algorithms_uninformed.py
├── algorithms_informed.py
├── algorithms_local.py
├── algorithms_complex.py
└── README.md
```

Ý nghĩa các file chính:

| File | Chức năng |
|---|---|
| `main.py` | Điểm chạy chính của chương trình |
| `ui.py` | Xây dựng giao diện Pygame, nút bấm, animation và log |
| `grid.py` | Quản lý trạng thái bảng, kiểm tra goal, sinh trạng thái kế tiếp |
| `utils.py` | Lớp `Node`, hàm truy vết đường đi, heuristic và hàm chi phí |
| `algorithms_uninformed.py` | Các thuật toán tìm kiếm không thông tin |
| `algorithms_informed.py` | Các thuật toán tìm kiếm có thông tin |
| `algorithms_local.py` | Các thuật toán tìm kiếm cục bộ |
| `algorithms_complex.py` | Các thuật toán trong môi trường phức tạp |

---

## 5. Cách cài đặt và chạy chương trình

### Bước 1: Cài Python

Cài Python phiên bản 3.10 trở lên. Có thể kiểm tra bằng lệnh:

```bash
python --version
```

### Bước 2: Cài Pygame

```bash
pip install pygame
```

### Bước 3: Chạy chương trình

Nếu đang đứng trong thư mục chứa file `main.py`, chạy:

```bash
python main.py
```

Nếu đang đứng ở thư mục gốc repository, chạy:

```bash
cd 8_puzzle
python main.py
```

### Phím điều khiển

| Thao tác | Chức năng |
|---|---|
| Phím mũi tên | Di chuyển ô số theo hướng tương ứng |
| `Xáo Trộn` | Tạo trạng thái mới bằng cách xáo trộn bảng |
| `Chơi Lại` | Đưa bảng về trạng thái ban đầu |
| `Dừng Lại` / `Tiếp Tục` | Tạm dừng hoặc tiếp tục animation |
| `ESC` | Thoát chương trình |

---

## 6. Các nhóm thuật toán đã cài đặt

Chương trình chia thuật toán thành 4 nhóm chính:

1. **Tìm kiếm không thông tin**
2. **Tìm kiếm có thông tin**
3. **Tìm kiếm cục bộ**
4. **Tìm kiếm trong môi trường phức tạp**

---

## 7. Nhóm thuật toán tìm kiếm không thông tin

Nhóm này không sử dụng heuristic để ước lượng khoảng cách đến đích. Thuật toán chỉ dựa vào cấu trúc không gian trạng thái và cách mở rộng nút.

### 7.1. BFS - Breadth-First Search

BFS mở rộng các trạng thái theo từng mức độ sâu. Trạng thái nào sinh ra trước ở mức nông hơn sẽ được xét trước.

Đặc điểm:

- Tìm được lời giải tối ưu theo số bước nếu mỗi bước có chi phí bằng nhau.
- Dễ hiểu, dễ cài đặt.
- Tốn bộ nhớ vì phải lưu nhiều trạng thái trong hàng đợi.

### 7.2. DFS - Depth-First Search

DFS đi sâu theo một nhánh trước, khi không đi tiếp được thì quay lui.

Đặc điểm:

- Bộ nhớ thường thấp hơn BFS.
- Có thể tìm được lời giải rất dài.
- Không đảm bảo lời giải tối ưu.
- Dễ đi sâu vào nhánh kém hiệu quả.

### 7.3. UCS - Uniform Cost Search

UCS chọn trạng thái có chi phí thấp nhất để mở rộng. Trong chương trình này, giá trị `g(n)` được biểu diễn bằng số ô sai vị trí so với trạng thái đích.

Đặc điểm:

- Có cơ chế ưu tiên trạng thái có chi phí thấp.
- Phù hợp khi các bước đi có chi phí khác nhau.
- Với cách cài đặt hiện tại, UCS không hoàn toàn giống UCS chuẩn theo chi phí đường đi, vì `g(n)` đang dựa vào số ô sai vị trí.

### 7.4. IDS - Iterative Deepening Search

IDS kết hợp ưu điểm của BFS và DFS. Thuật toán chạy Depth-Limited Search nhiều lần với giới hạn độ sâu tăng dần.

Đặc điểm:

- Tìm được lời giải tối ưu theo độ sâu nếu chi phí bước đi bằng nhau.
- Ít tốn bộ nhớ hơn BFS.
- Phải lặp lại việc duyệt các mức nông nhiều lần.

### 7.5. So sánh trong nhóm tìm kiếm không thông tin

| Thuật toán | Tối ưu lời giải | Đầy đủ | Bộ nhớ | Nhận xét |
|---|---:|---:|---:|---|
| BFS | Có | Có | Cao | Phù hợp bài toán nhỏ, lời giải ngắn |
| DFS | Không | Có nếu có kiểm soát trạng thái | Thấp hơn BFS | Có thể cho lời giải rất dài |
| UCS | Phụ thuộc hàm chi phí | Có | Trung bình đến cao | Tốt khi chi phí được định nghĩa phù hợp |
| IDS | Có | Có | Thấp | Cân bằng tốt giữa BFS và DFS |

Đánh giá chung: Trong nhóm này, **BFS** và **IDS** đáng tin cậy hơn khi cần lời giải ngắn nhất. **DFS** phù hợp để minh họa cơ chế duyệt sâu nhưng không nên dùng khi cần lời giải tối ưu. **UCS** có ý nghĩa khi hàm chi phí phản ánh đúng chi phí thực tế của đường đi.

---

## 8. Nhóm thuật toán tìm kiếm có thông tin

Nhóm này sử dụng heuristic để định hướng quá trình tìm kiếm. Heuristic chính trong chương trình là **Manhattan Distance**, tính tổng khoảng cách từ vị trí hiện tại của mỗi ô đến vị trí đích.

### 8.1. Greedy Best-First Search

Greedy chọn trạng thái có `h(n)` nhỏ nhất, tức là trạng thái được ước lượng gần đích nhất.

Đặc điểm:

- Tốc độ thường nhanh.
- Dễ bị mắc kẹt hoặc đi theo hướng tưởng tốt nhưng không tối ưu.
- Không đảm bảo lời giải ngắn nhất.

### 8.2. A* Search

A* sử dụng hàm đánh giá:

```text
f(n) = g(n) + h(n)
```

Trong đó:

- `g(n)` là chi phí đã đi.
- `h(n)` là chi phí ước lượng còn lại.

Trong chương trình này, `h(n)` là Manhattan Distance. Hàm `f_cost()` đang kết hợp số ô sai vị trí và Manhattan Distance để xếp ưu tiên.

Đặc điểm:

- Nếu cài đặt `g(n)` là chi phí đường đi thực tế và `h(n)` chấp nhận được, A* có thể tìm lời giải tối ưu.
- Thường hiệu quả hơn BFS vì có hướng tìm kiếm.
- Có thể tốn bộ nhớ khi không gian trạng thái lớn.

### 8.3. IDA* - Iterative Deepening A*

IDA* kết hợp tư tưởng của A* và IDS. Thuật toán dùng ngưỡng `f(n)` và tăng dần ngưỡng qua từng vòng lặp.

Đặc điểm:

- Tiết kiệm bộ nhớ hơn A*.
- Vẫn tận dụng heuristic để định hướng tìm kiếm.
- Có thể phải lặp lại nhiều trạng thái qua các vòng ngưỡng.

### 8.4. So sánh trong nhóm tìm kiếm có thông tin

| Thuật toán | Dựa vào | Tối ưu | Bộ nhớ | Nhận xét |
|---|---|---:|---:|---|
| Greedy | `h(n)` | Không | Trung bình | Nhanh nhưng dễ đi sai hướng |
| A* | `g(n) + h(n)` | Có nếu cài đặt chuẩn | Cao | Cân bằng giữa chi phí đã đi và ước lượng còn lại |
| IDA* | Ngưỡng `f(n)` | Có nếu heuristic phù hợp | Thấp hơn A* | Tốt khi muốn giảm bộ nhớ |

Đánh giá chung: **Greedy** phù hợp khi ưu tiên tốc độ và chấp nhận lời giải không tối ưu. **A*** thường là lựa chọn mạnh nhất nếu cần lời giải tốt. **IDA*** phù hợp khi muốn lợi thế của heuristic nhưng giảm áp lực bộ nhớ.

---

## 9. Nhóm thuật toán tìm kiếm cục bộ

Tìm kiếm cục bộ không duyệt toàn bộ cây trạng thái. Thuật toán chỉ quan tâm đến trạng thái hiện tại và các trạng thái lân cận. Nhóm này phù hợp để minh họa các khái niệm như cực trị địa phương, plateau, random restart và xác suất chấp nhận trạng thái xấu hơn.

### 9.1. Simple Hill Climbing

Simple Hill Climbing chọn trạng thái lân cận đầu tiên có heuristic tốt hơn hiện tại.

Đặc điểm:

- Nhanh, đơn giản.
- Dễ dừng ở cực trị địa phương.
- Không đảm bảo tìm được lời giải.

### 9.2. Steepest-Ascent Hill Climbing

Thuật toán xét tất cả trạng thái lân cận rồi chọn trạng thái tốt nhất.

Đặc điểm:

- Cẩn thận hơn Simple Hill Climbing.
- Mỗi bước tốn nhiều phép xét hơn.
- Vẫn có thể mắc kẹt ở cực trị địa phương.

### 9.3. Stochastic Hill Climbing

Thuật toán chọn ngẫu nhiên một trạng thái tốt hơn trong các trạng thái lân cận.

Đặc điểm:

- Có yếu tố ngẫu nhiên nên có thể tránh một số đường đi cố định kém hiệu quả.
- Kết quả mỗi lần chạy có thể khác nhau.
- Không đảm bảo tối ưu.

### 9.4. Random Restart Hill Climbing

Thuật toán chạy Hill Climbing nhiều lần từ các trạng thái khởi đầu khác nhau.

Đặc điểm:

- Giảm nguy cơ mắc kẹt tại cực trị địa phương.
- Tốn thời gian hơn Hill Climbing thường.
- Vẫn không đảm bảo chắc chắn tìm được lời giải.

### 9.5. Local Beam Search

Local Beam Search giữ đồng thời `k` trạng thái tốt nhất ở mỗi vòng lặp.

Đặc điểm:

- Tìm kiếm rộng hơn Hill Climbing.
- Có khả năng thoát khỏi một số nhánh kém.
- Tốn bộ nhớ hơn Hill Climbing đơn.

### 9.6. Simulated Annealing

Simulated Annealing cho phép chọn cả trạng thái xấu hơn với một xác suất nhất định, đặc biệt ở giai đoạn nhiệt độ cao.

Đặc điểm:

- Có khả năng thoát khỏi cực trị địa phương.
- Kết quả phụ thuộc vào nhiệt độ ban đầu, tốc độ làm nguội và yếu tố ngẫu nhiên.
- Không đảm bảo lời giải tối ưu.

### 9.7. So sánh trong nhóm tìm kiếm cục bộ

| Thuật toán | Có ngẫu nhiên | Khả năng thoát cực trị địa phương | Tốc độ | Độ ổn định |
|---|---:|---:|---:|---:|
| Simple Hill | Không | Thấp | Rất nhanh | Trung bình |
| Steepest Hill | Không | Thấp | Nhanh | Cao hơn Simple |
| Stochastic Hill | Có | Trung bình | Nhanh | Thấp hơn do ngẫu nhiên |
| Random Restart | Có | Cao hơn Hill thường | Trung bình | Khá tốt |
| Local Beam | Có khởi tạo ngẫu nhiên | Trung bình đến cao | Trung bình | Khá tốt |
| Simulated Annealing | Có | Cao nếu tham số phù hợp | Trung bình | Phụ thuộc tham số |

Đánh giá chung: Nhóm tìm kiếm cục bộ chạy nhanh và trực quan, nhưng không phù hợp nếu yêu cầu chắc chắn tìm được lời giải tối ưu. Trong nhóm này, **Local Beam Search**, **Random Restart** và **Simulated Annealing** có khả năng tìm lời giải tốt hơn các biến thể Hill Climbing đơn giản vì có cơ chế mở rộng hoặc thoát khỏi cực trị địa phương.

---

## 10. Nhóm thuật toán trong môi trường phức tạp

Nhóm này mô phỏng các tình huống khó hơn so với bài toán 8-Puzzle chuẩn, ví dụ không biết trạng thái đầu, chỉ quan sát được một phần trạng thái, hoặc dùng mô hình cây kế hoạch.

### 10.1. Search Without Start State

Thuật toán tìm ngược từ trạng thái đích về trạng thái hiện tại, sau đó đảo ngược chuỗi hành động để tạo lời giải từ trạng thái hiện tại đến đích.

Đặc điểm:

- Minh họa cách tìm kiếm khi không mở rộng trực tiếp từ trạng thái đầu.
- Vẫn tận dụng heuristic Manhattan để định hướng.
- Phù hợp để so sánh với hướng tìm kiếm thuận.

### 10.2. Partially Observable Search

Thuật toán chỉ quan sát một phần trạng thái, cụ thể là các ô `1, 2, 3, 4`. Heuristic chỉ tính trên các ô nhìn thấy.

Đặc điểm:

- Mô phỏng môi trường thiếu thông tin.
- Có thể tìm được lời giải nhưng đường đi thường dài hơn.
- Chất lượng phụ thuộc vào phần trạng thái quan sát được.

### 10.3. AND-OR Search

AND-OR Search thường dùng cho môi trường có tính bất định, trong đó:

- Nút OR biểu diễn việc chọn hành động.
- Nút AND biểu diễn việc phải xử lý tất cả kết quả có thể xảy ra.

Trong 8-Puzzle, môi trường là xác định, nên mỗi hành động chỉ sinh ra một kết quả. Vì vậy AND-OR Search trong chương trình chủ yếu dùng để minh họa mô hình cây kế hoạch.

### 10.4. Backtracking Search

Backtracking duyệt theo chiều sâu, thử một nhánh, nếu không phù hợp thì quay lui. Chương trình kết hợp thêm heuristic Manhattan để cắt bớt các nhánh kém.

Đặc điểm:

- Thể hiện rõ cơ chế thử sai và quay lui.
- Có thể cắt nhánh bằng điều kiện heuristic.
- Không phải lúc nào cũng cho lời giải tối ưu.

### 10.5. So sánh trong nhóm môi trường phức tạp

| Thuật toán | Mô hình chính | Ưu điểm | Hạn chế |
|---|---|---|---|
| Search Without Start State | Tìm ngược từ goal | Cho góc nhìn khác về không gian trạng thái | Cần biết rõ trạng thái đích và trạng thái cần khớp |
| Partially Observable | Quan sát một phần | Mô phỏng thiếu thông tin | Heuristic yếu hơn nên đường đi có thể dài hơn |
| AND-OR Search | Cây kế hoạch | Phù hợp lý thuyết môi trường bất định | Với 8-Puzzle xác định, vai trò AND chưa thể hiện mạnh |
| Backtracking | Thử và quay lui | Dễ hiểu, có thể cắt nhánh | Có thể tốn thời gian nếu không cắt nhánh tốt |

Đánh giá chung: Nhóm này không chỉ nhằm tìm lời giải nhanh nhất mà còn nhằm minh họa các biến thể môi trường tìm kiếm. **Search Without Start State** và **AND-OR Search** thường cho kết quả ổn định hơn trong 8-Puzzle xác định. **Partially Observable Search** cho thấy khi thiếu thông tin, lời giải có thể dài hơn. **Backtracking** phù hợp để minh họa cơ chế quay lui và cắt nhánh.

---

## 11. So sánh giữa các nhóm thuật toán

| Nhóm thuật toán | Có heuristic | Đảm bảo lời giải | Đảm bảo tối ưu | Bộ nhớ | Phù hợp nhất khi |
|---|---:|---:|---:|---:|---|
| Không thông tin | Không | Có với BFS/IDS | Có với BFS/IDS nếu chi phí đều | Trung bình đến cao | Không có thông tin định hướng |
| Có thông tin | Có | Có với A*/IDA* nếu cài đặt phù hợp | Có với A*/IDA* nếu heuristic phù hợp | Trung bình đến cao | Muốn tìm nhanh hơn BFS |
| Cục bộ | Có | Không chắc | Không | Thấp đến trung bình | Cần minh họa tối ưu cục bộ, chạy nhanh |
| Môi trường phức tạp | Tùy thuật toán | Tùy mô hình | Tùy thuật toán | Trung bình | Cần mô phỏng thiếu thông tin, tìm ngược, cây kế hoạch, quay lui |

### Nhận xét tổng quát

- **Nhóm không thông tin** là nền tảng, dễ hiểu, phù hợp để học cách duyệt không gian trạng thái.
- **Nhóm có thông tin** hiệu quả hơn vì dùng heuristic để ưu tiên trạng thái gần đích.
- **Nhóm cục bộ** nhanh nhưng không chắc chắn tìm được lời giải, đặc biệt dễ mắc kẹt tại cực trị địa phương.
- **Nhóm môi trường phức tạp** giúp mở rộng bài toán sang các tình huống thực tế hơn, nơi thông tin có thể thiếu hoặc mô hình hành động có thể phức tạp.

Nếu xét mục tiêu giải 8-Puzzle chuẩn, **BFS, IDS, A*** và **IDA*** là các lựa chọn đáng tin cậy hơn. Nếu xét mục tiêu minh họa nhiều chiến lược AI khác nhau, toàn bộ bốn nhóm thuật toán trong chương trình đều có giá trị riêng.

---

## 12. Kết quả tham khảo trên trạng thái mặc định

Bảng sau là kết quả tham khảo khi chạy từ trạng thái mặc định của chương trình. Với các thuật toán có yếu tố ngẫu nhiên, số bước có thể thay đổi giữa các lần chạy.

| Thuật toán | Số bước tham khảo | Đạt trạng thái đích | Nhận xét |
|---|---:|---:|---|
| BFS | 22 | Có | Lời giải ngắn và ổn định |
| DFS | Rất dài | Có | Tìm được nhưng không tối ưu |
| UCS | 30 | Có | Phụ thuộc cách định nghĩa `g(n)` |
| IDS | 22 | Có | Tương đương BFS về độ sâu lời giải, tiết kiệm bộ nhớ hơn |
| Greedy | 54 | Có | Nhanh nhưng không tối ưu |
| A* | 68 | Có | Kết quả phụ thuộc cách cài `f(n)` hiện tại |
| IDA* | 22 | Có | Cho lời giải tốt và tiết kiệm bộ nhớ |
| Simple Hill | 5 | Không | Dừng tại cực trị địa phương |
| Steepest Hill | 5 | Không | Cũng dễ mắc kẹt |
| Stochastic Hill | Thay đổi | Không ổn định | Phụ thuộc ngẫu nhiên |
| Random Restart | Thay đổi | Không ổn định | Tốt hơn Hill đơn nhưng vẫn không chắc chắn |
| Local Beam | Thay đổi | Có thể có | Giữ nhiều ứng viên nên mạnh hơn Hill đơn |
| Simulated Annealing | Thay đổi | Không ổn định | Phụ thuộc tham số nhiệt độ |
| Search Without Start State | 22 | Có | Tìm ngược từ goal cho kết quả tốt |
| Partially Observable | 40 | Có | Do thiếu thông tin nên đường đi dài hơn |
| AND-OR Search | 22 | Có | Ổn trong môi trường xác định |
| Backtracking | 24 | Có | Có quay lui và cắt nhánh |

---

## 13. Phân tích heuristic và hàm chi phí

Chương trình sử dụng hai đại lượng chính:

### Manhattan Distance - `h(n)`

```text
h(n) = tổng khoảng cách Manhattan của các ô số đến vị trí đích
```

Heuristic này phù hợp với 8-Puzzle vì mỗi bước chỉ di chuyển một ô theo chiều ngang hoặc dọc.

### Misplaced Tiles - số ô sai vị trí

```text
Số ô sai vị trí = số ô chưa nằm đúng vị trí đích, không tính ô trống
```

Trong chương trình, giá trị này được dùng như một dạng `g(n)` để hiển thị và xếp ưu tiên ở một số thuật toán. Riêng IDA* dùng `depth + h(n)` để bảo đảm chi phí tăng theo độ sâu tìm kiếm.

---

## 14. Ưu điểm của chương trình

- Giao diện trực quan, dễ thao tác.
- Có animation minh họa từng bước đi.
- Cài đặt nhiều thuật toán thuộc nhiều nhóm khác nhau.
- Có log quá trình chạy và giá trị đánh giá.
- Phù hợp để học các chiến lược tìm kiếm trong Trí tuệ nhân tạo.
- Có thể so sánh trực tiếp kết quả giữa các thuật toán trên cùng một trạng thái.

---

## 15. Hạn chế và hướng phát triển

### Hạn chế

- Một số thuật toán cục bộ không đảm bảo tìm được lời giải.
- Kết quả của thuật toán ngẫu nhiên có thể thay đổi giữa các lần chạy.
- UCS và A* trong chương trình dùng cách tính chi phí phục vụ minh họa, chưa hoàn toàn giống định nghĩa chuẩn nếu xét chi phí đường đi thực tế.
- Chưa có bảng thống kê tự động thời gian chạy, số nút mở rộng và bộ nhớ sử dụng cho tất cả thuật toán.

### Hướng phát triển

- Bổ sung thống kê thời gian chạy cho từng thuật toán.
- Đếm số nút đã mở rộng và kích thước frontier lớn nhất.
- Cho phép người dùng nhập trạng thái ban đầu tùy ý.
- Kiểm tra tính giải được của trạng thái 8-Puzzle trước khi chạy thuật toán.
- Chuẩn hóa lại `g(n)` của UCS và A* theo chi phí đường đi thực tế.
- Xuất kết quả so sánh ra file CSV hoặc Excel.

---

## 16. Kết luận

Dự án 8-Puzzle này không chỉ giải một trò chơi trượt số đơn giản mà còn minh họa nhiều nhóm thuật toán tìm kiếm quan trọng trong Trí tuệ nhân tạo. Qua việc so sánh các thuật toán trong cùng nhóm và khác nhóm, có thể thấy rằng không có thuật toán nào tốt nhất cho mọi tình huống.

- Khi cần lời giải chắc chắn và ngắn: nên dùng **BFS**, **IDS**, **A*** hoặc **IDA***.
- Khi cần minh họa duyệt sâu: có thể dùng **DFS** và **Backtracking**.
- Khi cần minh họa heuristic: nên dùng **Greedy**, **A***, **IDA***.
- Khi cần minh họa cực trị địa phương và ngẫu nhiên: nên dùng nhóm **Hill Climbing**, **Local Beam**, **Simulated Annealing**.
- Khi cần mô phỏng môi trường thiếu thông tin hoặc phức tạp: dùng **Partially Observable Search**, **AND-OR Search** và **Search Without Start State**.

Chương trình phù hợp làm bài thực hành, bài báo cáo hoặc demo môn Trí tuệ nhân tạo về chủ đề tìm kiếm trong không gian trạng thái.
