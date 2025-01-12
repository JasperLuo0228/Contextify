import SwiftUI
import AVFoundation

struct ExtractedTerm: Identifiable, Equatable {
    let id = UUID()
    let term: String
    let definition: String
    let isName: Bool
    let news: [NewsItem]?
    
    let courseCode: String?
    let courseName: String?
    let isCourse: Bool

    static func == (lhs: ExtractedTerm, rhs: ExtractedTerm) -> Bool {
        lhs.term == rhs.term &&
        lhs.definition == rhs.definition &&
        lhs.isName == rhs.isName &&
        lhs.courseCode == rhs.courseCode &&
        lhs.courseName == rhs.courseName &&
        lhs.isCourse == rhs.isCourse
    }
}

struct NewsItem: Identifiable {
    let id = UUID()
    let title: String
    let summary: String
    let imageURL: String
}

struct ContentView: View {
    @State private var isRecording: Bool = false
    @State private var showTranscript: Bool = true
    @State private var transcribedText: [String] = []
    @State private var extractedTerms: [ExtractedTerm] = []

    @State private var webSocketTask: URLSessionWebSocketTask?
    @State private var isConnected: Bool = false

    private let audioEngine = AVAudioEngine()

    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(showTranscript ? "Hide Transcript" : "Show Transcript")
                    .fontWeight(.bold)
                    .foregroundColor(.blue)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .onTapGesture {
                        withAnimation {
                            showTranscript.toggle()
                        }
                    }

                Text(isRecording ? (isConnected ? "Listening" : "Connecting...") : "Stopped")
                    .fontWeight(.bold)
                    .foregroundColor(
                        isRecording
                        ? (isConnected ? .green : .yellow)
                        : .red
                    )
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }
            .padding(.horizontal)

            if showTranscript {
                ZStack(alignment: .topLeading) {
                    Color(colorScheme == .dark ? .white : .gray)
                        .opacity(colorScheme == .dark ? 0.15 : 0.05)
                        .cornerRadius(10)

                    ScrollViewReader { proxy in
                        ScrollView {
                            VStack(alignment: .leading, spacing: 10) {
                                ForEach(Array(transcribedText.enumerated()), id: \.offset) { (index, line) in
                                    Text(line)
                                        .font(.body)
                                        .foregroundColor(.primary)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                        .multilineTextAlignment(.leading)
                                        .transition(.opacity)
                                        .id(index)
                                }
                                Spacer()
                            }
                            .padding()
                            .onChange(of: transcribedText) { _ in
                                withAnimation(.easeInOut(duration: 0.4)) {
                                    if let lastIndex = transcribedText.indices.last {
                                        proxy.scrollTo(lastIndex, anchor: .bottom)
                                    }
                                }
                            }
                        }
                    }
                }
                .frame(
                    width: UIScreen.main.bounds.width * 0.9,
                    height: UIScreen.main.bounds.height * 0.15,
                    alignment: .topLeading
                )
                .padding()

                Divider()
                    .frame(height: 2)
                    .background(
                        colorScheme == .dark
                        ? Color.white.opacity(0.15)
                        : Color.gray.opacity(0.3)
                    )
                    .padding(.horizontal)
            }

            ScrollViewReader { proxy in
                ScrollView {
                    VStack(spacing: 20) {
                        ForEach(extractedTerms, id: \.id) { term in
                            if term.isCourse {
                                CourseCardView(term: term)
                                    .transition(.move(edge: .trailing))
                                    .animation(.easeInOut, value: extractedTerms)
                            } else if let newsItems = term.news, !newsItems.isEmpty {
                                CompanyCardView(term: term, news: newsItems)
                                    .transition(.move(edge: .trailing))
                                    .animation(.easeInOut, value: extractedTerms)
                            } else {
                                StandardCardView(term: term)
                                    .transition(.move(edge: .trailing))
                                    .animation(.easeInOut, value: extractedTerms)
                            }
                        }
                        Spacer()
                    }
                    .frame(
                        width: UIScreen.main.bounds.width * 0.9
                    )
                    .onChange(of: extractedTerms) { _ in
                        withAnimation(.easeInOut(duration: 0.4)) {
                            if let last = extractedTerms.last {
                                proxy.scrollTo(last.id, anchor: .bottom)
                            }
                        }
                    }
                }
                .padding()
            }

            Button(action: {
                if isRecording {
                    stopRecording()
                    disconnectWebSocket()
                } else {
                    connectWebSocket()
                    startRecording()
                }
                isRecording.toggle()
            }) {
                Text(isRecording ? "STOP" : "START")
                    .font(.system(size: 18, weight: .bold))
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(isRecording ? Color.red : Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            .padding()
        }
        .padding()
    }
}

extension ContentView {
    func startRecording() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .default, options: .allowBluetooth)
            try audioSession.setActive(true)

            let inputNode = audioEngine.inputNode
            let recordingFormat = inputNode.outputFormat(forBus: 0)

            inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
                self.audioBufferHandler(buffer: buffer)
            }

            try audioEngine.start()
            print("Audio engine started")
        } catch {
            print("Error starting audio engine: \(error)")
        }
    }

    func stopRecording() {
        audioEngine.inputNode.removeTap(onBus: 0)
        audioEngine.stop()
        print("Audio engine stopped")
    }

    func audioBufferHandler(buffer: AVAudioPCMBuffer) {
        guard let task = webSocketTask else { return }

        let audioData = buffer.audioBufferList.pointee.mBuffers.mData
        let dataSize = Int(buffer.audioBufferList.pointee.mBuffers.mDataByteSize)
        if let audioPointer = audioData, dataSize > 0 {
            let audioBytes = Data(bytes: audioPointer, count: dataSize)
            let message = URLSessionWebSocketTask.Message.data(audioBytes)

            task.send(message) { error in
                if let error = error {
                    print("WebSocket send error: \(error)")
                    DispatchQueue.main.async {
                        self.isConnected = false
                        self.isRecording = false
                    }
                }
            }
        }
    }

    func connectWebSocket() {
        let url = URL(string: "ws://47.251.94.96:8000/ws/audio")!
        let task = URLSession.shared.webSocketTask(with: url)
        webSocketTask = task

        task.resume()
        receiveWebSocketMessages(task: task)

        DispatchQueue.main.async {
            self.isConnected = true
        }
        print("WebSocket connection initiated")
    }

    func disconnectWebSocket() {
        webSocketTask?.cancel(with: .normalClosure, reason: nil)
        webSocketTask = nil
        DispatchQueue.main.async {
            self.isConnected = false
        }
        print("WebSocket connection closed")
    }

    func receiveWebSocketMessages(task: URLSessionWebSocketTask) {
        task.receive { result in
            switch result {
            case .success(let message):
                switch message {
                case .data(let data):
                    parseJsonAndUpdateUI(from: data)

                case .string(let text):
                    if let data = text.data(using: .utf8) {
                        if let _ = try? JSONSerialization.jsonObject(with: data, options: []) {
                            parseJsonAndUpdateUI(from: data)
                        } else {
                            DispatchQueue.main.async {
                                self.transcribedText.append(text)
                            }
                        }
                    } else {
                        DispatchQueue.main.async {
                            self.transcribedText.append(text)
                        }
                    }

                @unknown default:
                    break
                }

            case .failure(let error):
                print("WebSocket receive error: \(error)")
                DispatchQueue.main.async {
                    self.isConnected = false
                    self.isRecording = false
                }
            }

            self.receiveWebSocketMessages(task: task)
        }
    }

    func parseJsonAndUpdateUI(from data: Data) {
        guard let json = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] else {
            return
        }

        DispatchQueue.main.async {
            let transcriptionText = json["transcription"] as? String ?? ""
            if !transcriptionText.isEmpty {
                self.transcribedText.append(transcriptionText)
            }

            let courseDescriptions = json["course_descriptions"] as? [[String: Any]] ?? []
            for c in courseDescriptions {
                let code = c["course_code"] as? String ?? "UnknownCode"
                let name = c["course_name"] as? String ?? "UnknownCourseName"
                let desc = c["description"] as? String ?? "No description"

                let extracted = ExtractedTerm(
                    term: "",
                    definition: desc,
                    isName: false,
                    news: nil,
                    courseCode: code,
                    courseName: name,
                    isCourse: true
                )
                self.extractedTerms.append(extracted)
            }

            let personDescriptions = json["person_descriptions"] as? [[String: Any]] ?? []
            for p in personDescriptions {
                let personName = p["person_name"] as? String ?? "Unknown Person"
                let bio = p["description"] as? String ?? "No bio"

                let extracted = ExtractedTerm(
                    term: personName,
                    definition: bio,
                    isName: true,
                    news: nil,
                    courseCode: nil,
                    courseName: nil,
                    isCourse: false
                )
                self.extractedTerms.append(extracted)
            }

            let technicalTerms = json["technical_term_definitions"] as? [[String: Any]] ?? []
            for t in technicalTerms {
                let term = t["term"] as? String ?? "Unknown TechTerm"
                let definition = t["description"] as? String ?? "No definition"

                let extracted = ExtractedTerm(
                    term: term,
                    definition: definition,
                    isName: false,
                    news: nil,
                    courseCode: nil,
                    courseName: nil,
                    isCourse: false
                )
                self.extractedTerms.append(extracted)
            }

            let companyDetails = json["company_details"] as? [[String: Any]] ?? []
            for comp in companyDetails {
                let companyName = comp["company_name"] as? String ?? "Unknown Company"
                let description = comp["description"] as? String ?? "No company info"

                if let newsArray = comp["news"] as? [[String: Any]] {
                    var newsItems: [NewsItem] = []
                    for n in newsArray {
                        let title = n["title"] as? String ?? ""
                        let summary = n["summary"] as? String ?? ""
                        let imageURL = n["image_url"] as? String ?? ""
                        newsItems.append(NewsItem(title: title, summary: summary, imageURL: imageURL))
                    }

                    let extracted = ExtractedTerm(
                        term: companyName,
                        definition: description,
                        isName: false,
                        news: newsItems.isEmpty ? nil : newsItems,
                        courseCode: nil,
                        courseName: nil,
                        isCourse: false
                    )
                    self.extractedTerms.append(extracted)

                } else {
                    let extracted = ExtractedTerm(
                        term: companyName,
                        definition: description,
                        isName: false,
                        news: nil,
                        courseCode: nil,
                        courseName: nil,
                        isCourse: false
                    )
                    self.extractedTerms.append(extracted)
                }
            }
        }
    }
}

struct StandardCardView: View {
    let term: ExtractedTerm

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(term.term)
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.primary)

            Text(term.definition)
                .font(.body)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(term.isName ? Color.blue.opacity(0.1) : Color.gray.opacity(0.1))
        .cornerRadius(10)
    }
}

struct CompanyCardView: View {
    let term: ExtractedTerm
    let news: [NewsItem]

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(term.term)
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.primary)

            Text(term.definition)
                .font(.body)
                .foregroundColor(.secondary)

            ForEach(news) { item in
                Divider()
                HStack(alignment: .top, spacing: 10) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text(item.title)
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.primary)
                        Text(item.summary)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                    if let url = URL(string: item.imageURL) {
                        AsyncImage(url: url) { phase in
                            switch phase {
                            case .empty:
                                ProgressView()
                            case .success(let image):
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 60, height: 60)
                                    .cornerRadius(8)
                            case .failure:
                                Image(systemName: "photo")
                                    .resizable()
                                    .frame(width: 60, height: 60)
                            @unknown default:
                                EmptyView()
                            }
                        }
                    }
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(term.isName ? Color.blue.opacity(0.1) : Color.gray.opacity(0.1))
        .cornerRadius(10)
    }
}

struct CourseCardView: View {
    let term: ExtractedTerm

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(term.courseCode ?? "UnknownCode")
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.primary)

            Text(term.courseName ?? "UnknownCourseName")
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.primary)

            Text(term.definition)
                .font(.body)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(10)
    }
}

//#Preview {
//    ContentView()
//
