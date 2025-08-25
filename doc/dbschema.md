```prisma
// api/prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum TaskStatus { backlog in_progress blocked done }
enum Priority { low normal high critical }
enum Role { admin ops_manager engineer logistics executive viewer }
enum RigType { jackup semisub drillship }
enum RecordStatus { active archived }
enum MilestoneType { spud section_td casing cement bop_test completion other }

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  timezone  String?  @default("UTC")
  active    Boolean  @default(true)
  roles     UserRole[]
  tasks     Task[]   @relation("TaskAssignee")
  comments  TaskComment[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model UserRole {
  user   User @relation(fields: [userId], references: [id])
  userId String
  role   Role
  @@id([userId, role])
}

model Campaign {
  id         String   @id @default(uuid())
  name       String
  block      String?
  field      String?
  startDate  DateTime?
  endDate    DateTime?
  status     RecordStatus @default(active)
  rigs       Rig[]
  wells      Well[]
  tasks      Task[]
  createdBy  String?
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
}

model Rig {
  id         String   @id @default(uuid())
  campaign   Campaign @relation(fields: [campaignId], references: [id])
  campaignId String
  name       String
  type       RigType
  lat        Decimal? @db.Decimal(9,6)
  lon        Decimal? @db.Decimal(9,6)
  status     String?
  notes      String?
}

model Well {
  id         String   @id @default(uuid())
  campaign   Campaign @relation(fields: [campaignId], references: [id])
  campaignId String
  name       String
  status     String?
  startDate  DateTime?
  endDate    DateTime?
  plannedTdM Decimal? @db.Decimal(12,2)
  actualTdM  Decimal? @db.Decimal(12,2)
  milestones Milestone[]
  ddrs       Ddr[]
  nptEvents  NptEvent[]
  tasks      Task[]
}

model Milestone {
  id        String        @id @default(uuid())
  well      Well          @relation(fields: [wellId], references: [id])
  wellId    String
  type      MilestoneType
  plannedAt DateTime?
  actualAt  DateTime?
  eta       DateTime?
  status    RecordStatus  @default(active)
  notes     String?
}

model Task {
  id          String      @id @default(uuid())
  campaign    Campaign    @relation(fields: [campaignId], references: [id])
  campaignId  String
  well        Well?       @relation(fields: [wellId], references: [id])
  wellId      String?
  title       String
  description String?
  status      TaskStatus  @default(backlog)
  priority    Priority    @default(normal)
  labels      String[]
  dueAt       DateTime?
  assignee    User?       @relation("TaskAssignee", fields: [assigneeId], references: [id])
  assigneeId  String?
  version     Int         @default(1)
  deletedAt   DateTime?
  comments    TaskComment[]
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
  @@index([campaignId, status])
}

model TaskComment {
  id        String   @id @default(uuid())
  task      Task     @relation(fields: [taskId], references: [id])
  taskId    String
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  body      String
  createdAt DateTime @default(now())
}

model Attachment {
  id          String   @id @default(uuid())
  ownerType   String
  ownerId     String
  filename    String
  contentType String
  size        Int
  s3Key       String
  sha256      String?
  uploadedBy  String
  createdAt   DateTime @default(now())
}

model Ddr {
  id          String   @id @default(uuid())
  well        Well     @relation(fields: [wellId], references: [id])
  wellId      String
  reportDate  DateTime
  mdM         Decimal? @db.Decimal(12,2)
  tvdM        Decimal? @db.Decimal(12,2)
  ropMPerHr   Decimal? @db.Decimal(12,2)
  nptHours    Decimal? @db.Decimal(6,2)
  nptCategory String?
  remarks     String?
  version     Int      @default(1)
  @@unique([wellId, reportDate])
}

model NptEvent {
  id          String   @id @default(uuid())
  well        Well     @relation(fields: [wellId], references: [id])
  wellId      String
  startAt     DateTime
  endAt       DateTime
  category    String
  severity    Int
  description String?
}

model AuditLog {
  id        BigInt   @id @default(autoincrement())
  actorId   String?
  entity    String
  entityId  String
  action    String
  before    Json?
  after     Json?
  at        DateTime @default(now())
}

model WebhookSubscription {
  id      String  @id @default(uuid())
  url     String
  event   String
  secret  String
  active  Boolean @default(true)
}

model IdempotencyKey {
  key        String   @id
  firstSeen  DateTime @default(now())
  expiresAt  DateTime
}
// api/prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum TaskStatus { backlog in_progress blocked done }
enum Priority { low normal high critical }
enum Role { admin ops_manager engineer logistics executive viewer }
enum RigType { jackup semisub drillship }
enum RecordStatus { active archived }
enum MilestoneType { spud section_td casing cement bop_test completion other }

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  timezone  String?  @default("UTC")
  active    Boolean  @default(true)
  roles     UserRole[]
  tasks     Task[]   @relation("TaskAssignee")
  comments  TaskComment[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model UserRole {
  user   User @relation(fields: [userId], references: [id])
  userId String
  role   Role
  @@id([userId, role])
}

model Campaign {
  id         String   @id @default(uuid())
  name       String
  block      String?
  field      String?
  startDate  DateTime?
  endDate    DateTime?
  status     RecordStatus @default(active)
  rigs       Rig[]
  wells      Well[]
  tasks      Task[]
  createdBy  String?
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
}

model Rig {
  id         String   @id @default(uuid())
  campaign   Campaign @relation(fields: [campaignId], references: [id])
  campaignId String
  name       String
  type       RigType
  lat        Decimal? @db.Decimal(9,6)
  lon        Decimal? @db.Decimal(9,6)
  status     String?
  notes      String?
}

model Well {
  id         String   @id @default(uuid())
  campaign   Campaign @relation(fields: [campaignId], references: [id])
  campaignId String
  name       String
  status     String?
  startDate  DateTime?
  endDate    DateTime?
  plannedTdM Decimal? @db.Decimal(12,2)
  actualTdM  Decimal? @db.Decimal(12,2)
  milestones Milestone[]
  ddrs       Ddr[]
  nptEvents  NptEvent[]
  tasks      Task[]
}

model Milestone {
  id        String        @id @default(uuid())
  well      Well          @relation(fields: [wellId], references: [id])
  wellId    String
  type      MilestoneType
  plannedAt DateTime?
  actualAt  DateTime?
  eta       DateTime?
  status    RecordStatus  @default(active)
  notes     String?
}

model Task {
  id          String      @id @default(uuid())
  campaign    Campaign    @relation(fields: [campaignId], references: [id])
  campaignId  String
  well        Well?       @relation(fields: [wellId], references: [id])
  wellId      String?
  title       String
  description String?
  status      TaskStatus  @default(backlog)
  priority    Priority    @default(normal)
  labels      String[]
  dueAt       DateTime?
  assignee    User?       @relation("TaskAssignee", fields: [assigneeId], references: [id])
  assigneeId  String?
  version     Int         @default(1)
  deletedAt   DateTime?
  comments    TaskComment[]
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
  @@index([campaignId, status])
}

model TaskComment {
  id        String   @id @default(uuid())
  task      Task     @relation(fields: [taskId], references: [id])
  taskId    String
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  body      String
  createdAt DateTime @default(now())
}

model Attachment {
  id          String   @id @default(uuid())
  ownerType   String
  ownerId     String
  filename    String
  contentType String
  size        Int
  s3Key       String
  sha256      String?
  uploadedBy  String
  createdAt   DateTime @default(now())
}

model Ddr {
  id          String   @id @default(uuid())
  well        Well     @relation(fields: [wellId], references: [id])
  wellId      String
  reportDate  DateTime
  mdM         Decimal? @db.Decimal(12,2)
  tvdM        Decimal? @db.Decimal(12,2)
  ropMPerHr   Decimal? @db.Decimal(12,2)
  nptHours    Decimal? @db.Decimal(6,2)
  nptCategory String?
  remarks     String?
  version     Int      @default(1)
  @@unique([wellId, reportDate])
}

model NptEvent {
  id          String   @id @default(uuid())
  well        Well     @relation(fields: [wellId], references: [id])
  wellId      String
  startAt     DateTime
  endAt       DateTime
  category    String
  severity    Int
  description String?
}

model AuditLog {
  id        BigInt   @id @default(autoincrement())
  actorId   String?
  entity    String
  entityId  String
  action    String
  before    Json?
  after     Json?
  at        DateTime @default(now())
}

model WebhookSubscription {
  id      String  @id @default(uuid())
  url     String
  event   String
  secret  String
  active  Boolean @default(true)
}

model IdempotencyKey {
  key        String   @id
  firstSeen  DateTime @default(now())
  expiresAt  DateTime
}