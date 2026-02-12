# DNS Configuration for Fasthosts

## Add careflowai subdomain to veraldlabs.co.uk

---

## Method 1: Fasthosts Control Panel

### Step 1: Login to Fasthosts
1. Go to https://www.fasthosts.co.uk/login
2. Login with your Fasthosts account

### Step 2: Manage Domain
1. Go to **Domains** → **Manage Domains**
2. Find **veraldlabs.co.uk** and click **Manage**

### Step 3: Add DNS Records
1. Click **DNS** or **Manage DNS**
2. Click **Add DNS Record**

### Record 1: Frontend Subdomain
- **Type**: CNAME
- **Hostname**: careflowai
- **Target**: cname.railway.app
- **TTL**: 3600 (or default)
- Click **Add**

### Record 2: Backend API Subdomain
- **Type**: CNAME
- **Hostname**: api.careflowai
- **Target**: cname.railway.app
- **TTL**: 3600 (or default)
- Click **Add**

### Step 4: Save Changes
- Click **Save Changes** or **Update DNS**

---

## Method 2: Via Your Hosting Panel (if accessible)

If you see "Manage subdomains" in your hosting panel:

1. Login to your hosting control panel
2. Go to **Subdomain** → **Manage subdomains**
3. Click **Add Subdomain**

### Subdomain 1:
- **Subdomain**: careflowai
- **Destination**: CNAME → cname.railway.app
- Click **Add**

### Subdomain 2:
- **Subdomain**: api.careflowai
- **Destination**: CNAME → cname.railway.app
- Click **Add**

---

## Summary of DNS Records to Add:

| Type  | Name/Hostname      | Target              | TTL  |
|-------|--------------------|---------------------|------|
| CNAME | careflowai         | cname.railway.app   | 3600 |
| CNAME | api.careflowai     | cname.railway.app   | 3600 |

---

## What Happens Next:

1. **DNS Propagation** (10-30 minutes)
   - The DNS records will spread across the internet
   - Check status at: https://dnschecker.org/

2. **After Deployment to Railway**:
   - Railway will recognize the custom domain
   - SSL certificate will be auto-provisioned by Railway
   - Your existing SSL from Fasthosts is for the main domain only

---

## Verify DNS is Working:

### Check Online:
1. Go to https://dnschecker.org/
2. Enter: `careflowai.veraldlabs.co.uk`
3. Should show pointing to `cname.railway.app`

### Check via Command Line:
```bash
# Windows Command Prompt
nslookup careflowai.veraldlabs.co.uk

# Should show something like:
# cname.railway.app
# [Railway IP address]
```

---

## After DNS Configuration:

1. ✅ **DNS records added** (this step)
2. ⏳ **Wait for propagation** (10-30 min)
3. 🔜 **Deploy to Railway** (see QUICK_START_DEPLOYMENT.md)
4. 🔜 **Add custom domains in Railway**
5. ✅ **Website accessible** at careflowai.veraldlabs.co.uk

---

## Important Notes:

### About SSL Certificates:
- **Fasthosts SSL**: Covers veraldlabs.co.uk (main domain)
- **Railway SSL**: Auto-provided for careflowai.veraldlabs.co.uk (subdomain)
- Both work independently - no conflict

### About Google Search:
- Once deployed, Google will discover careflowai.veraldlabs.co.uk through:
  - DNS records
  - Backlinks from other sites
  - Manual submission to Google Search Console

- For faster indexing, after deployment:
  1. Go to https://search.google.com/search-console
  2. Add property: careflowai.veraldlabs.co.uk
  3. Submit sitemap: https://careflowai.veraldlabs.co.uk/sitemap.xml

---

## Troubleshooting:

### DNS Not Propagating:
- Wait 30 minutes and check again
- Clear your browser cache
- Check with https://dnschecker.org/

### Can't Add CNAME:
- Some hosts restrict CNAME records
- Contact Fasthosts support if needed

### "Record Already Exists":
- Delete existing records for careflowai/api.careflowai
- Re-add with correct target

---

## Next Steps:

1. **Add DNS records** in Fasthosts (follow steps above)
2. **Verify propagation** at https://dnschecker.org/
3. **Deploy to Railway** (see QUICK_START_DEPLOYMENT.md)

---

Need help? Contact Fasthosts support: https://www.fasthosts.co.uk/support
