請根據我提供的內容整理一下變成一份相對正式的 SRS.md

在我目前接觸py redis的情況下，時常會用到傳輸影像、聲音 通常只會用到 set/get, pub/sub，所以我才設計這款 redis-toolkit lib,目的不是要取代原本的 redis lib，而是根據我們的情境減少樣板工作和重複的工作時間，支援斷線重新連線，管理 sub/pub連線