# Claude Code Feature Workflow MVP

Küçük değişiklikler için doğrudan ana oturum; kapsamlı feature için ayrı mimar,
implementer ve isteğe bağlı reviewer. Slash command dosyaları
`.claude/commands/` içindedir. Kaydedilen feature akışında ana Claude oturumu
koordinatördür; bağımsız modül araştırmaları paralel, bağımlı aşamalar sıralı çalışır.

## Gereksinimler ve kurulum

- Güncel Claude Code, hesabınıza açık Opus/Sonnet modelleri.
- Python 3.9+ (`python3`) ve Git. Windows: WSL önerilir.
- Uygulamanızın mevcut Git repository'si; paket uygulama iskeleti içermez.

ZIP'i açın. İçinden çıkan `claude-feature-mvp` dizinindeki kurucuyu çalıştırın:

```bash
python3 /tam/yol/claude-feature-mvp/install.py /tam/yol/projeniz
```

Kurucu mevcut CLAUDE.md'ye yönergeleri ekler, mevcut settings.json'u korur.
Aynı isimli farklı agent/command dosyası varsa yazmadan hata verir. Önceki
sürüm kurulu bir projede değişen dosyalar için de bu koruma geçerlidir; yeni
talimatları mevcut dosyalarla karşılaştırıp elle birleştirin.
Mevcut project settings/user settings/managed settings geçerlidir; kurucu
izinleri sıfırlamaz. Paketteki yeni settings.json normal `default` modundadır.
Komutların yürütülmesi sırasında normal Claude Code tool izinleri sorulabilir.

Kurulum değişikliklerini gözden geçirip kendi Git akışınızla commit edin.
İlk implementation öncesinde uygulama/config çalışma ağacı temiz olmalıdır;
`docs/features/` raporları bu kontrolden hariçtir. Önceden var olan kaynak
kod değişiklikleri feature'a karışmasın diye bu kontrol konmuştur.

Proje kökünde Claude Code'u yeniden başlatın; `/agents` içinde altı agent'ı,
slash menüsünde altı komutu doğrulayın. VS Code entegre terminalinde `claude`
ile aynı akış kullanılabilir. Kurulu CLI varsa `claude --version` kontrol edin.
Model erişimi yoksa agent dosyalarındaki `model` alanını `inherit` yapabilirsiniz.
Projenizde build/test tarifleri özelse `.claude/project-context.md` içine yazın.

## Kullanım

Küçük bug, metin/stil değişikliği veya mevcut mimariye uyan açık bir ekleme:

```text
/feature-fast Profil sayfasındaki yanlış başlığı düzelt.
```

Ana oturum kodu değiştirir, ilgili kontrolleri çalıştırır ve kısa sonuç verir.
Plan, feature state veya ayrı agent çağrısı oluşturmaz. Auth/yetkilendirme,
ödeme, veri kaybı, migrasyon riski veya tasarımı belirsiz modüller arası işler
için aşağıdaki kaydedilen akışı kullanın. Dosya sayısı tek başına risk ölçüsü değildir.

```text
/feature-plan user-export Kullanıcı listesini CSV olarak dışa aktarmak istiyorum. Yalnızca adminler kullanabilsin.
```

Gerekirse birbirinden bağımsız modüller salt okunur researcher agent'larıyla
paralel incelenir. Planner mevcut kodu ve bulguları doğrulayarak dört temel
bölümlük plan oluşturur; uygulama kodunu değiştirmez.
Ana oturum `docs/features/user-export/plan.md` dosyasını kaydeder ve durur.
Planı okuyun; planlama aşamasında revizyon isteyebilirsiniz. Hazır planı
uygulamadan önce revize ettiyseniz implement komutu güncel hash'i onaylar.

```text
/feature-implement user-export
```

Bu komut kaydedilmiş güncel planın onayıdır. Koordinatör planın giriş noktalarını,
ilgili sembolleri, kararları ve test komutlarını implementer'a aktarır. Implementer
bunları kodda doğrular, kodu/testleri değiştirir ve gerekli kontrolleri çalıştırır.
Mevcut mimarideki yerel isimlendirme ve yardımcı fonksiyon kararlarını kendisi
verir; davranış, API, bağımlılık veya veri modelini değiştiren kararlarda durur.
Reviewer otomatik başlamaz.

```text
/feature-review user-export
/feature-status user-export
```

Review sadece rapor üretir. Findings varsa otomatik düzeltme yapılmaz; raporu
izleyerek ayrıca düzeltme isteyin. Aynı plan içindeki küçük düzeltmeleri normal
Claude isteğiyle yapıp tekrar review çalıştırabilirsiniz; implementation.md'deki
kanıt/check sonuçlarını da güncelletin. Mimari/kapsam değişirse yeni slug ile
planlayın. Rapor zamanına ait verdict, sonraki değişiklikleri kapsamaz.

Yarım kalan in_progress/blocked feature için aynı implement komutu devam eder.
Başka feature'a geçmeden aktif/blocked işi tamamlayın; tamamen bırakılacak bir
feature'ın kaynak değişiklikleri ve state'i manuel olarak, gözden geçirilerek
arşivlenmelidir. MVP otomatik rollback/abandon komutu içermez.
Bir feature için aynı çalışma dizininde eşzamanlı Claude oturumu kullanmayın.
Bağımsız işler için ayrı Git worktree kullanın.

## Dosya yapısı

```text
claude-feature-mvp/
  README.md
  CLAUDE.md
  install.py
  .claude/
    settings.json
    project-context.md
    agents/
      architecture-planner.md
      feature-researcher.md
      feature-implementer.md
      feature-reviewer.md
      project-reviewer.md
      refactor-implementer.md
    commands/
      feature-fast.md
      feature-plan.md
      feature-implement.md
      feature-review.md
      feature-status.md
    workflows/feature.md
    scripts/feature_state.py
  tests/test_mvp.py
  tests/test_project_review.py
```

Çalışınca proje içinde `docs/features/<slug>/` altında request.md, plan.md,
state.json, implementation.md ve isteğe bağlı review.md oluşur.
Bu raporlar oturumlar arasında görev bağlamını taşır; gizli anahtar yazmayın.

## Model ve yetki seçimi

| Rol | Model alias | Araçlar | Sonuç |
| --- | --- | --- | --- |
| Mimar | opus | Read, Grep, Glob | Kod kanıtına dayalı plan |
| Araştırmacı | inherit | Read, Grep, Glob | Bağımsız modül bulguları |
| Implementer | sonnet | Read, Grep, Glob, Edit, Write, Bash | Kod + test + handoff |
| Reviewer | opus | Read, Grep, Glob | Bağımsız inceleme raporu |
| Refactor implementer | sonnet | Read, Grep, Glob, Edit, Write, Bash | Seçili review bulguları için kod + test + handoff |

Bu seçim bir başlangıç politikasıdır; alias'lar provider/hesap erişimine göre
çözümlenir. Maliyet azaltmak için reviewer'ı sonnet, tüm rolleri inherit yapabilirsiniz.
Planner/researcher/reviewer shell ve yazma araçlarına sahip değildir. Raporları koordinatör
kaydeder. Tool allowlist ile normal izin modu farklı mekanizmalardır.

Model değişikliğinden önce birkaç benzer görevde planlama, uygulama, test ve
raporlama sürelerini ayrı kaydedin. Yeniden okuma ve düzeltme turlarını da sayın;
yalnız tek agent çağrısının süresine göre model değiştirmeyin. Önce kısa akışın
toplam süreye etkisini görün, sonra model seçeneklerini aynı görev türlerinde
karşılaştırın.

## Doğrulama

Paket dizininde:

```bash
python3 -m unittest discover -s tests -v
```

Testler gerçek geçici Git repository'lerinde kurulum, durum geçişleri, kirli
kaynak engeli, hash değişikliği, eşzamanlı feature engeli ve resume'ı kontrol eder.
Canlı Claude Code testi: `/feature-fast` ile küçük bir değişiklik yapıp ayrı
agent/feature raporu oluşmadığını ve ilgili kontrolün çalıştığını doğrulayın.
Ardından kapsamlı bir feature planlayın; kaynak dosyalarının
değişmediğini kontrol edin; implement çağrısında Sonnet agent'ı ve test sonuçlarını
doğrulayın; review çağırmadan reviewer'ın çalışmadığını doğrulayın; sonra review
çağırıp yalnız rapor üretildiğini kontrol edin. Yeni oturumda status çalıştırın.

Canlı Claude Code agent çağrısı otomatik testlerin kapsamında değildir.
Paketin statik biçimi ve Python/Git davranışı test edilmiştir; kendi projenizin
build/test sonuçları kurulumdan sonra gerçek feature çalışmasında oluşur.

## MVP sınırları

Prompt tabanlı koordinasyon ve Python state guard kullanılır. Helper onaylanan
planın hash'ini kontrol eder; arbitrary kod editlerini yakalayan hook yoktur.
Dolayısıyla bu, ana Claude oturumunun tüm yazmalarını kilitleyen bir güvenlik
sınırı değildir. Test başarıları helper tarafından yorumlanmaz; koordinatör
rapordaki kanıta göre implemented/blocked seçer. Rapor dosyaları elle değiştirilebilir.
Review mevcut HEAD'e göre tüm uygulama diff'ini ve untracked dosyaları kapsar;
implementation sırasında commit/branch değişimi yapılmamalıdır. Sonrasında review
istiyorsanız açık baseline ile manuel inceleme gerekir. Ignore edilen kaynak
dosyalar Git diff'ine girmez; projede bu tür dosyaları açıkça scope'a ekleyin.

## Resmi kaynaklar

11 Ekim 2026 tarihinde kontrol edilen dokümanlar:
- https://code.claude.com/docs/en/slash-commands
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/settings

Commands ve skills aynı slash arayüzünü üretir; mevcut `.claude/commands/`
biçimi desteklenir. Daha sonra supporting files gerektiğinde skills biçimine
geçilebilir; bu MVP için gerekli değildir.

## Yeni: proje mimarisi ve kod kalitesi incelemesi

```text
/project-review
/project-review src/backend
/project-review src/auth/login.ts
```

Parametre gerçek repo-relative dosya/dizin yoludur. Önce mimari çıkarılır, sonra
kod dosyaları sırayla incelenir. Clean code, sorumluluk ayrımı, coupling, duplication,
hata yönetimi ve mimari antipattern bulguları kanıt ve önem sırasıyla raporlanır.
Yalnız rapor yazılır; uygulama kodunda düzeltme yapılmaz.

Yeni dosyalar: .claude/commands/project-review.md, agents/project-reviewer.md,
workflows/project-review.md, project-review.json, scripts/project_review_snapshot.py
ve templates/project-review-report.md (tümü .claude altında).
Project reviewer Opus kullanır; yalnız Read/Grep/Glob araçları vardır.

Review sonrasında düzeltmek istediğiniz finding ID'lerini veya açıkça sınırlanmış
onarım kapsamını belirterek `refactor-implementer` agent'ını kullanabilirsiniz.
Agent bulguyu güncel kodda yeniden doğrular, kullanıcı değişikliklerini korur,
yalnızca onaylı kapsamı uygular ve ilgili testleri çalıştırır. Belirsiz ürün
kararlarında `NEEDS_INPUT`, plansız geniş mimari değişikliklerde `NEEDS_PLAN`
döner; review bulgularını otomatik veya topluca uygulamaz.

Raporlar `docs/reviews/<UTC-timestamp>/` altında architecture.md, code-quality.md,
report.md, dosya envanteri ve batch raporlarıyla saklanır. İlk/son fingerprint
farklıysa STALE; eksik inceleme varsa INCOMPLETE bildirilir. Büyük projeler sırayla
batch'lere bölünür; okunmayan dosyalar açıkça kapsam tablosunda görünür.

Bu SonarQube entegrasyonu değildir. Mevcut yerel lint/static analyzer'lar varsa,
komutları okuyarak kurulum/düzeltme yapmayan check modunda kullanılır. Yoksa açıkça
bildirilir. Complexity/coverage/duplication yüzdesi, debt süresi ve quality gate
ölçüm olmadan üretilmez. Kurallar gerçek proje yapısına göre gerekçelendirilir;
kişisel stil tercihleri bug sayılmaz. Bulgular severity ve confidence ile raporlanır.

Git-ignore dosyaları kapsam dışıdır. node_modules/vendor/build varsayılan hariçtir;
el yazımı kaynaklarınız buralardaysa config'i güncelleyin. UTF-8 olmayan, binary,
çok büyük ve symlink dosyalar ayrıca kaydedilir. Review raporları feature başlangıcı
clean-source kontrolüne takılabilir: yeni feature başlamadan raporları kendi Git
akışınızla commit edin veya güvenli biçimde çalışma ağacından ayırın.

Önceki MVP kuruluysa yeni ZIP'teki install.py değişmiş dosyalarda durur;
yeni talimatları mevcut proje dosyalarıyla karşılaştırıp birleştirin.
Mevcut ayarlar ve feature dosyaları korunur.
Project reviewer agent'ının görünmesi için Claude Code'u yeniden başlatın.

Canlı deneme: /project-review çalıştırın; architecture raporunun code phase'den önce
üretildiğini, coverage ile inventory'nin uyuştuğunu, bulguların gerçek satırlara
işaret ettiğini ve product dosyalarının değişmediğini kontrol edin.

Paket doğrulaması: 13 Python/Git testi geçti. Önceki ZIP üzerinden kurulmuş projeye
yeni modülün eklenmesi ayrıca kontrol edildi. Canlı Claude Code agent denemesi
otomatik testlerin kapsamında değildir.
