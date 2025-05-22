# Face Detection & Recognition System Design

## 1. Data Flow Diagram (DFD)

### Level 0 DFD
```mermaid
graph LR
    User <--> System[Face Detection & Recognition System]
    System <--> DB[(Database)]
```

### Level 1 DFD
```mermaid
graph TD
    Camera[Camera Input] --> FaceDetect[Face Detection]
    User --> FaceDetect
    FaceDetect --> FaceRecog[Face Recognition]
    FaceRecog --> DB[(Database)]
    FaceRecog --> Display[Display Results]
```

## 2. Entity Relationship (ER) Diagram
```mermaid
erDiagram
    User ||--o{ Face_Data : has
    User ||--o{ Detection_Log : generates
    
    User {
        int user_id PK
        string name
        string email
        string password
        datetime created_at
    }
    
    Face_Data {
        int face_id PK
        int user_id FK
        blob face_encodings
        datetime date_added
        datetime last_updated
    }
    
    Detection_Log {
        int log_id PK
        int user_id FK
        datetime timestamp
        float confidence
        string location
    }
```

## 3. Database Table Design

### Users Table
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Face_Data Table
```sql
CREATE TABLE face_data (
    face_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    face_encodings BLOB NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Detection_Log Table
```sql
CREATE TABLE detection_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT,
    location VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 4. Form Designs

### User Registration Form
```mermaid
graph TD
    subgraph User_Registration_Form
        Title[User Registration]
        Name[Name Input Field]
        Email[Email Input Field]
        Password[Password Input Field]
        Submit[Submit Button]
        
        Title --> Name
        Name --> Email
        Email --> Password
        Password --> Submit
    end
```

### Face Registration Form
```mermaid
graph TD
    subgraph Face_Registration_Form
        Title[Face Registration]
        Camera[Camera Preview Window]
        UserID[User ID Input Field]
        ButtonGroup[Button Group]
        Capture[Capture]
        Save[Save]
        Cancel[Cancel]
        
        Title --> Camera
        Camera --> UserID
        UserID --> ButtonGroup
        ButtonGroup --> Capture
        ButtonGroup --> Save
        ButtonGroup --> Cancel
    end
```

### Face Detection Interface
```mermaid
graph TD
    subgraph Face_Detection_Interface
        Title[Face Detection]
        Feed[Live Camera Feed]
        Status[Detection Status]
        Confidence[Confidence Level]
        Controls[Control Buttons]
        Start[Start]
        Stop[Stop]
        Settings[Settings]
        
        Title --> Feed
        Feed --> Status
        Status --> Confidence
        Confidence --> Controls
        Controls --> Start
        Controls --> Stop
        Controls --> Settings
    end
```

## 5. System Architecture

```mermaid
graph TB
    subgraph Input_Module
        Camera[Camera Interface]
        ImageCapture[Image Capture]
        VideoProcess[Real-time Video Processing]
    end

    subgraph Processing_Module
        FaceDetect[Face Detection Algorithm]
        FaceRecog[Face Recognition Model]
        Preprocess[Image Preprocessing]
        Features[Feature Extraction]
    end

    subgraph Storage_Module
        DB[(Database)]
        Encodings[Face Encodings]
        UserData[User Management]
    end

    subgraph Output_Module
        Display[Real-time Display]
        Results[Recognition Results]
        UI[User Interface]
        Alerts[Notifications]
    end

    Input_Module --> Processing_Module
    Processing_Module --> Storage_Module
    Processing_Module --> Output_Module
    Storage_Module --> Processing_Module
```

### Component Details

1. **Input Module**
   - Camera interface
   - Image capture
   - Real-time video processing

2. **Processing Module**
   - Face detection algorithm
   - Face recognition model
   - Image preprocessing
   - Feature extraction

3. **Storage Module**
   - Database management
   - Face encodings storage
   - User data management

4. **Output Module**
   - Real-time display
   - Recognition results
   - User interface
   - Alerts and notifications

## 6. Technical Stack

- **Frontend**: Python with OpenCV for UI
- **Backend**: Python
- **Database**: SQLite/MySQL
- **Libraries**:
  - OpenCV for image processing
  - dlib for face detection
  - face_recognition for face recognition
  - numpy for numerical operations
