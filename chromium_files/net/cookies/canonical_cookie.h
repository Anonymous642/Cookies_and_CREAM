// Copyright 2012 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef NET_COOKIES_CANONICAL_COOKIE_H_
#define NET_COOKIES_CANONICAL_COOKIE_H_

#include <iomanip>
#include <memory>
#include <string>
#include <tuple>
#include <vector>

#include "base/feature_list.h"
#include "base/gtest_prod_util.h"
#include "base/strings/string_piece.h"
#include "base/time/time.h"
#include "base/types/pass_key.h" 
#include "net/base/features.h"
#include "net/base/net_export.h"
#include "net/cookies/cookie_access_result.h"
#include "net/cookies/cookie_constants.h"
#include "net/cookies/cookie_inclusion_status.h"
#include "net/cookies/cookie_options.h"
#include "net/cookies/cookie_partition_key.h"
#include "net/http/http_util.h"
#include "third_party/abseil-cpp/absl/types/optional.h"
#include "url/third_party/mozilla/url_parse.h"

class GURL;

namespace net {

class ParsedCookie;
class CanonicalCookie;

struct CookieWithAccessResult;
struct CookieAndLineWithAccessResult;

using CookieList = std::vector<CanonicalCookie>;
using CookieAndLineAccessResultList =
    std::vector<CookieAndLineWithAccessResult>;
using CookieAccessResultList = std::vector<CookieWithAccessResult>;

struct NET_EXPORT CookieAccessParams {
  CookieAccessParams() = delete;
  CookieAccessParams(CookieAccessSemantics access_semantics,
                     bool delegate_treats_url_as_trustworthy);

  // |access_semantics| is the access mode of the cookie access check.
  CookieAccessSemantics access_semantics = CookieAccessSemantics::UNKNOWN;
  // |delegate_treats_url_as_trustworthy| should be true iff the
  // CookieAccessDelegate has authorized access to secure cookies from URLs
  // which might not otherwise be able to do so.
  bool delegate_treats_url_as_trustworthy = false;
};

// BrowserOnly - the new monitored data object
struct MonitoredData {
  CookieMonitored level_;
  int count_;
  std::vector<std::string> changelog_;
  std::string expected_;

  MonitoredData();
  MonitoredData(const MonitoredData& other);
  MonitoredData(MonitoredData&& other);
  MonitoredData& operator=(const MonitoredData& other);
  MonitoredData& operator=(MonitoredData&& other);

  MonitoredData(CookieMonitored level, std::string expected);

  MonitoredData(CookieMonitored level,
	       int count, 
	       std::vector<std::string> changelog,
	       std::string expected);

  ~MonitoredData();
};

class NET_EXPORT CanonicalCookie {
 public:
  // StrictlyUniqueCookieKey always populates the cookie's source scheme and
  // source port.
  using StrictlyUniqueCookieKey = std::tuple<absl::optional<CookiePartitionKey>,
                                             /*name=*/std::string,
                                             /*domain=*/std::string,
                                             /*path=*/std::string,
                                             CookieSourceScheme,
                                             /*source_port=*/int>;

  // Conditionally populates the source scheme and source port depending on the
  // state of their associated feature.
  using UniqueCookieKey = std::tuple<absl::optional<CookiePartitionKey>,
                                     /*name=*/std::string,
                                     /*domain=*/std::string,
                                     /*path=*/std::string,
                                     absl::optional<CookieSourceScheme>,
                                     /*source_port=*/absl::optional<int>>;

  CanonicalCookie();
  CanonicalCookie(const CanonicalCookie& other);
  CanonicalCookie(CanonicalCookie&& other);
  CanonicalCookie& operator=(const CanonicalCookie& other);
  CanonicalCookie& operator=(CanonicalCookie&& other);
  ~CanonicalCookie();

  // This constructor does not validate or canonicalize their inputs;
  // the resulting CanonicalCookies should not be relied on to be canonical
  // unless the caller has done appropriate validation and canonicalization
  // themselves.
  // NOTE: Prefer using CreateSanitizedCookie() over directly using this
  // constructor.
  CanonicalCookie(base::PassKey<CanonicalCookie>,
                  std::string name,
                  std::string value,
                  std::string domain,
                  std::string path,
                  base::Time creation,
                  base::Time expiration,
                  base::Time last_access,
                  base::Time last_update,
                  bool secure,
                  bool httponly,
		  bool browseronly, // BrowserOnly - add new atributes to decleration
                  CookieSameSite same_site,
                  CookiePriority priority,
                  absl::optional<CookiePartitionKey> partition_key,
		  MonitoredData monitored_data,
                  CookieSourceScheme scheme_secure = CookieSourceScheme::kUnset,
                  int source_port = url::PORT_UNSPECIFIED);

  // Creates a new |CanonicalCookie| from the |cookie_line| and the
  // |creation_time|.  Canonicalizes inputs.  May return nullptr if
  // an attribute value is invalid.  |url| must be valid.  |creation_time| may
  // not be null. Sets optional |status| to the relevant CookieInclusionStatus
  // if provided.  |server_time| indicates what the server sending us the Cookie
  // thought the current time was when the cookie was produced.  This is used to
  // adjust for clock skew between server and host.
  //
  // SameSite and HttpOnly related parameters are not checked here,
  // so creation of CanonicalCookies with e.g. SameSite=Strict from a cross-site
  // context is allowed. Create() also does not check whether |url| has a secure
  // scheme if attempting to create a Secure cookie. The Secure, SameSite, and
  // HttpOnly related parameters should be checked when setting the cookie in
  // the CookieStore.
  //
  // The partition_key argument only needs to be present if the cookie line
  // contains the Partitioned attribute. If the cookie line will never contain
  // that attribute, you should use absl::nullopt to indicate you intend to
  // always create an unpartitioned cookie. If partition_key has a value but the
  // cookie line does not contain the Partitioned attribute, the resulting
  // cookie will be unpartitioned. If the partition_key is null, then the cookie
  // will be unpartitioned even when the cookie line has the Partitioned
  // attribute.
  //
  // The `block_truncated` argument indicates whether the '\0', '\n', and '\r'
  // characters should cause the cookie to fail to be created if present
  // (instead of truncating `cookie_line` at the first occurrence).
  //
  // If a cookie is returned, |cookie->IsCanonical()| will be true.
  static std::unique_ptr<CanonicalCookie> Create(
      const GURL& url,
      const std::string& cookie_line,
      const base::Time& creation_time,
      absl::optional<base::Time> server_time,
      absl::optional<CookiePartitionKey> cookie_partition_key,
      bool block_truncated = true,
      CookieInclusionStatus* status = nullptr);

  // Create a canonical cookie based on sanitizing the passed inputs in the
  // context of the passed URL.  Returns a null unique pointer if the inputs
  // cannot be sanitized.  If `status` is provided it will have any relevant
  // CookieInclusionStatus rejection reasons set. If a cookie is created,
  // `cookie->IsCanonical()` will be true.
  static std::unique_ptr<CanonicalCookie> CreateSanitizedCookie(
      const GURL& url,
      const std::string& name,
      const std::string& value,
      const std::string& domain,
      const std::string& path,
      base::Time creation_time,
      base::Time expiration_time,
      base::Time last_access_time,
      bool secure,
      bool http_only,
      //bool browser_only,
      CookieSameSite same_site,
      CookiePriority priority,
      absl::optional<CookiePartitionKey> partition_key,
      CookieInclusionStatus* status = nullptr,
      const CookieMonitored monitored_level = Cookie_Monitored_NONE, // BrowserOnly add new atributes to decleration and default to none/off
      const std::string& monitor = std::string());

  // FromStorage is a factory method which is meant for creating a new
  // CanonicalCookie using properties of a previously existing cookie
  // that was already ingested into the cookie store.
  // This should NOT be used to create a new CanonicalCookie that was not
  // already in the store.
  // Returns nullptr if the resulting cookie is not canonical,
  // i.e. cc->IsCanonical() returns false.
  static std::unique_ptr<CanonicalCookie> FromStorage(
      std::string name,
      std::string value,
      std::string domain,
      std::string path,
      base::Time creation,
      base::Time expiration,
      base::Time last_access,
      base::Time last_update,
      bool secure,
      bool httponly,
      CookieSameSite same_site,
      CookiePriority priority,
      absl::optional<CookiePartitionKey> partition_key,
      CookieSourceScheme source_scheme,
      int source_port);//,
      //MonitoredData monitored_number);

  // Create a CanonicalCookie that is not guaranteed to actually be Canonical
  // for tests. This factory should NOT be used in production.
  static std::unique_ptr<CanonicalCookie> CreateUnsafeCookieForTesting(
      const std::string& name,
      const std::string& value,
      const std::string& domain,
      const std::string& path,
      const base::Time& creation,
      const base::Time& expiration,
      const base::Time& last_access,
      const base::Time& last_update,
      bool secure,
      bool httponly,
      CookieSameSite same_site,
      CookiePriority priority,
      absl::optional<CookiePartitionKey> partition_key = absl::nullopt,
      CookieSourceScheme scheme_secure = CookieSourceScheme::kUnset,
      int source_port = url::PORT_UNSPECIFIED);

  bool operator<(const CanonicalCookie& other) const {
    // Use the cookie properties that uniquely identify a cookie to determine
    // ordering.
    return UniqueKey() < other.UniqueKey();
  }

  bool operator==(const CanonicalCookie& other) const {
    return IsEquivalent(other);
  }

  const std::string& Name() const { return name_; }
  const std::string& Value() const { return value_; }
  // We represent the cookie's host-only-flag as the absence of a leading dot in
  // Domain(). See IsDomainCookie() and IsHostCookie() below.
  // If you want the "cookie's domain" as described in RFC 6265bis, use
  // DomainWithoutDot().
  const std::string& Domain() const { return domain_; }
  const std::string& Path() const { return path_; }
  const base::Time& CreationDate() const { return creation_date_; }
  const base::Time& ExpiryDate() const { return expiry_date_; }
  const base::Time& LastAccessDate() const { return last_access_date_; }
  const base::Time& LastUpdateDate() const { return last_update_date_; }
  bool IsPersistent() const { return !expiry_date_.is_null(); }
  bool IsSecure() const { return secure_; }
  bool IsHttpOnly() const { return httponly_; }
  bool IsBrowserOnly() const { return browseronly_; } // BrowserOnly - browseronly getter
  CookieSameSite SameSite() const { return same_site_; }
  CookiePriority Priority() const { return priority_; }
  bool IsPartitioned() const { return partition_key_.has_value(); }
  const absl::optional<CookiePartitionKey>& PartitionKey() const {
    return partition_key_;
  }
 
  // BrowserOnly - monitored attribute behavior
  bool IsMonitored() const {return monitored_data_.level_ != Cookie_Monitored_NONE;}
  CookieMonitored MonitoredLevel() const {return monitored_data_.level_;}
  bool IsCounting() const {return (monitored_data_.level_ == Cookie_Monitored_HIGH_COUNT || monitored_data_.level_ == Cookie_Monitored_LOW_COUNT);} //optional
  int MonitoredCount() const {return monitored_data_.count_;} //optional
  const std::vector<std::string>& MonitoredChangelog() const {return monitored_data_.changelog_;}
  void MonitoredChangelogStr(std::string* output) const {
    std::string log = "[";
    for (auto entry = monitored_data_.changelog_.begin(); entry != monitored_data_.changelog_.end(); entry++){
      log = log + *entry;
      if (entry + 1 != monitored_data_.changelog_.end())
        log = log + ", ";
    }
    log = log + "]";
    *output = log;
  }

  void MonitoredSettings(std::string* output) const {
    std::string current = "{\"V\":\"" + value_ + "\",\"D\":\"" + domain_ + "\",\"P\":\"" + path_ + "\",\"E\":";
    std::string expires = std::to_string(expiry_date_.InSecondsFSinceUnixEpoch());
    if(expires.find('.') != std::string::npos){
      expires = expires.substr(0, expires.find_last_not_of('0') + 1);
      if (expires.find('.') == expires.size() - 1){
        expires = expires.substr(0, expires.size() - 1);
      }
    }
    current = current + expires + ",\"S\":";
    if (secure_){
      current = current + "1,\"H\":";
    }else{
      current = current + "0,\"H\":";
    }
    if (httponly_){
      current = current + "1,\"B\":";
    }else{
      current = current + "0,\"B\":";
    }
    if(browseronly_){
      current = current + "1,\"PT\":";
    }else{
      current = current + "0,\"PT\":";
    }
    if (partition_key_.has_value()){
      current = current + "1,\"SS\":";
    }else{
      current = current + "0,\"SS\":";
    }
    switch (same_site_){
      case CookieSameSite::NO_RESTRICTION:
        current = current + "0}";
	break;
      case CookieSameSite::LAX_MODE:
	current = current + "1}";
	break;
      case CookieSameSite::STRICT_MODE:
	current = current + "2}";
	break;
      case CookieSameSite::UNSPECIFIED:
	current = current + "3}";
	break;
    }
    *output = current;
  }

  const std::string& MonitoredExpected() const {return monitored_data_.expected_;}

  void UpdateCount() {monitored_data_.count_++;} // optional
  void SetCount(int count) {monitored_data_.count_ = count;} //optional
  void setMonitoredLevel(CookieMonitored level) {monitored_data_.level_ = level;}
  void UpdateChangelog(std::string entry) {monitored_data_.changelog_.push_back(entry);}
  void SetChangelog(std::vector<std::string> changelog) {monitored_data_.changelog_ = std::move(changelog);} 
  void UpdateExpected(std::string expected) {monitored_data_.expected_ = std::move(expected);}
  
  // Returns an enum indicating the scheme of the origin that
  // set this cookie. This is not part of the cookie spec but is being used to
  // collect metrics for a potential change to the cookie spec
  // (https://tools.ietf.org/html/draft-west-cookie-incrementalism-01#section-3.4)
  CookieSourceScheme SourceScheme() const { return source_scheme_; }
  // Returns the port of the origin that originally set this cookie (the
  // source port). This is not part of the cookie spec but is being used to
  // collect metrics for a potential change to the cookie spec.
  int SourcePort() const { return source_port_; }
  bool IsDomainCookie() const {
    return !domain_.empty() && domain_[0] == '.'; }
  bool IsHostCookie() const { return !IsDomainCookie(); }

  // Returns whether this cookie is Partitioned and its partition key matches a
  // a same-site context by checking if the cookies domain site is the same as
  // the partition key's site.
  // Returns false if the cookie has no partition key.
  bool IsFirstPartyPartitioned() const;

  // Returns whether the cookie is partitioned in a third-party context.
  bool IsThirdPartyPartitioned() const;

  // Returns the cookie's domain, with the leading dot removed, if present.
  // This corresponds to the "cookie's domain" as described in RFC 6265bis.
  std::string DomainWithoutDot() const;

  bool IsExpired(const base::Time& current) const {
    return !expiry_date_.is_null() && current >= expiry_date_;
  }

  // Are the cookies considered equivalent in the eyes of RFC 2965.
  // The RFC says that name must match (case-sensitive), domain must
  // match (case insensitive), and path must match (case sensitive).
  // For the case insensitive domain compare, we rely on the domain
  // having been canonicalized (in
  // GetCookieDomainWithString->CanonicalizeHost).
  // If partitioned cookies are enabled, then we check the cookies have the same
  // partition key in addition to the checks in RFC 2965.
  bool IsEquivalent(const CanonicalCookie& ecc) const {
    // It seems like it would make sense to take secure, httponly, and samesite
    // into account, but the RFC doesn't specify this.
    // NOTE: Keep this logic in-sync with TrimDuplicateCookiesForKey().
    return UniqueKey() == ecc.UniqueKey();
  }

  StrictlyUniqueCookieKey StrictlyUniqueKey() const {
    return std::make_tuple(partition_key_, name_, domain_, path_,
                           source_scheme_, source_port_);
  }

  // Returns a key such that two cookies with the same UniqueKey() are
  // guaranteed to be equivalent in the sense of IsEquivalent().
  // The `partition_key_` field will always be nullopt when partitioned cookies
  // are not enabled.
  // The source_scheme and source_port fields depend on whether or not their
  // associated features are enabled.
  UniqueCookieKey UniqueKey() const;

  // Checks a looser set of equivalency rules than 'IsEquivalent()' in order
  // to support the stricter 'Secure' behaviors specified in Step 12 of
  // https://tools.ietf.org/html/draft-ietf-httpbis-rfc6265bis-05#section-5.4
  // which originated from the proposal in
  // https://tools.ietf.org/html/draft-ietf-httpbis-cookie-alone#section-3
  //
  // Returns 'true' if this cookie's name matches |secure_cookie|, and this
  // cookie is a domain-match for |secure_cookie| (or vice versa), and
  // |secure_cookie|'s path is "on" this cookie's path (as per 'IsOnPath()').
  // If partitioned cookies are enabled, it also checks that the cookie has
  // the same partition key as |secure_cookie|.
  //
  // Note that while the domain-match cuts both ways (e.g. 'example.com'
  // matches 'www.example.com' in either direction), the path-match is
  // unidirectional (e.g. '/login/en' matches '/login' and '/', but
  // '/login' and '/' do not match '/login/en').
  //
  // Conceptually:
  // If new_cookie.IsEquivalentForSecureCookieMatching(secure_cookie) is true,
  // this means that new_cookie would "shadow" secure_cookie: they would would
  // be indistinguishable when serialized into a Cookie header. This is
  // important because, if an attacker is attempting to set new_cookie, it
  // should not be allowed to mislead the server into using new_cookie's value
  // instead of secure_cookie's.
  //
  // The reason for the asymmetric path comparison ("cookie1=bad; path=/a/b"
  // from an insecure source is not allowed if "cookie1=good; secure; path=/a"
  // exists, but "cookie2=bad; path=/a" from an insecure source is allowed if
  // "cookie2=good; secure; path=/a/b" exists) is because cookies in the Cookie
  // header are serialized with longer path first. (See CookieSorter in
  // cookie_monster.cc.) That is, they would be serialized as "Cookie:
  // cookie1=bad; cookie1=good" in one case, and "Cookie: cookie2=good;
  // cookie2=bad" in the other case. The first scenario is not allowed because
  // the attacker injects the bad value, whereas the second scenario is ok
  // because the good value is still listed first.
  bool IsEquivalentForSecureCookieMatching(
      const CanonicalCookie& secure_cookie) const;

  // Returns true if the |other| cookie's data members (instance variables)
  // match, for comparing cookies in colletions.
  bool HasEquivalentDataMembers(const CanonicalCookie& other) const {
    return creation_date_ == other.creation_date_ &&
           last_access_date_ == other.last_access_date_ &&
           expiry_date_ == other.expiry_date_ && secure_ == other.secure_ &&
           httponly_ == other.httponly_ && same_site_ == other.same_site_ &&
           priority_ == other.priority_ && 
	   browseronly_ == other.browseronly_ && // BrowserOnly - add browseronly to equality check but not monitored as not to leak anything
           partition_key_ == other.partition_key_ && name_ == other.name_ &&
           value_ == other.value_ && domain_ == other.domain_ &&
           path_ == other.path_ &&
           last_update_date_ == other.last_update_date_ &&
           source_scheme_ == other.source_scheme_ &&
           source_port_ == other.source_port_;
  }

  // Similar to operator<, but considers all data members.
  bool DataMembersPrecede(const CanonicalCookie& other) const {
    auto f = [](const CanonicalCookie& c) {
      return std::tie(c.creation_date_, c.last_access_date_, c.expiry_date_,
                      c.secure_, c.httponly_, c.browseronly_, c.same_site_, // BrowserOnly - same here
		      c.priority_, c.partition_key_, c.name_, c.value_, 
		      c.domain_, c.path_, c.last_update_date_, c.source_scheme_, 
		      c.source_port_);
    };
    return f(*this) < f(other);
  }

  void SetSourceScheme(CookieSourceScheme source_scheme) {
    source_scheme_ = source_scheme;
  }

  // Set the source port value. Performs a range check and sets the port to
  // url::PORT_INVALID if value isn't in [0,65535] or url::PORT_UNSPECIFIED.
  void SetSourcePort(int port);

  void SetLastAccessDate(const base::Time& date) {
    last_access_date_ = date;
  }
  void SetCreationDate(const base::Time& date) { creation_date_ = date; }

  // Returns true if the given |url_path| path-matches this cookie's cookie-path
  // as described in section 5.1.4 in RFC 6265. This returns true if |path_| and
  // |url_path| are identical, or if |url_path| is a subdirectory of |path_|.
  bool IsOnPath(const std::string& url_path) const;

  // This returns true if this cookie's |domain_| indicates that it can be
  // accessed by |host|.
  //
  // In the case where |domain_| has no leading dot, this is a host cookie and
  // will only domain match if |host| is identical to |domain_|.
  //
  // In the case where |domain_| has a leading dot, this is a domain cookie. It
  // will match |host| if |domain_| is a suffix of |host|, or if |domain_| is
  // exactly equal to |host| plus a leading dot.
  //
  // Note that this isn't quite the same as the "domain-match" algorithm in RFC
  // 6265bis, since our implementation uses the presence of a leading dot in the
  // |domain_| string in place of the spec's host-only-flag. That is, if
  // |domain_| has no leading dot, then we only consider it matching if |host|
  // is identical (which reflects the intended behavior when the cookie has a
  // host-only-flag), whereas the RFC also treats them as domain-matching if
  // |domain_| is a subdomain of |host|.
  bool IsDomainMatch(const std::string& host) const;

  // Returns if the cookie should be included (and if not, why) for the given
  // request |url| using the CookieInclusionStatus enum. HTTP only cookies can
  // be filter by using appropriate cookie |options|.
  //
  // PLEASE NOTE that this method does not check whether a cookie is expired or
  // not!
  CookieAccessResult IncludeForRequestURL(
      const GURL& url,
      const CookieOptions& options,
      const CookieAccessParams& params) const;

  // Returns if the cookie with given attributes can be set in context described
  // by |options| and |params|, and if no, describes why.
  //
  // |cookie_access_result| is an optional input status, to allow for status
  // chaining from callers. It helps callers provide the status of a
  // canonical cookie that may have warnings associated with it.
  CookieAccessResult IsSetPermittedInContext(
      const GURL& source_url,
      const CookieOptions& options,
      const CookieAccessParams& params,
      const std::vector<std::string>& cookieable_schemes,
      const absl::optional<CookieAccessResult>& cookie_access_result =
          absl::nullopt) const;

  std::string DebugString() const;

  // Returns the canonical path based on the specified url and path attribute
  // value. Note that this method does not enforce character set or size
  // checks on `path_string`.
  static std::string CanonPathWithString(const GURL& url,
                                         const std::string& path_string);

  // Returns a "null" time if expiration was unspecified or invalid.
  static base::Time ParseExpiration(const ParsedCookie& pc,
                                    const base::Time& current,
                                    const base::Time& server_time);

  // Per rfc6265bis the maximum expiry date is no further than 400 days in the
  // future.
  static base::Time ValidateAndAdjustExpiryDate(
      const base::Time& expiry_date,
      const base::Time& creation_date);

  // Cookie ordering methods.

  // Returns true if the cookie is less than |other|, considering only name,
  // domain and path. In particular, two equivalent cookies (see IsEquivalent())
  // are identical for PartialCompare().
  bool PartialCompare(const CanonicalCookie& other) const;

  // Return whether this object is a valid CanonicalCookie().  Invalid
  // cookies may be constructed by the detailed constructor.
  // A cookie is considered canonical if-and-only-if:
  // * It can be created by CanonicalCookie::Create, or
  // * It is identical to a cookie created by CanonicalCookie::Create except
  //   that the creation time is null, or
  // * It can be derived from a cookie created by CanonicalCookie::Create by
  //   entry into and retrieval from a cookie store (specifically, this means
  //   by the setting of an creation time in place of a null creation time, and
  //   the setting of a last access time).
  // An additional requirement on a CanonicalCookie is that if the last
  // access time is non-null, the creation time must also be non-null and
  // greater than the last access time.
  bool IsCanonical() const;

  // Return whether this object is a valid CanonicalCookie() when retrieving the
  // cookie from the persistent store. Cookie that exist in the persistent store
  // may have been created before more recent changes to the definition of
  // "canonical". To ease the transition to the new definitions, and to prevent
  // users from having their cookies deleted, this function supports the older
  // definition of canonical. This function is intended to be temporary because
  // as the number of older cookies (which are non-compliant with the newer
  // definition of canonical) decay toward zero it can eventually be replaced
  // by `IsCanonical()` to enforce the newer definition of canonical.
  //
  // A cookie is considered canonical by this function if-and-only-if:
  // * It is considered canonical by IsCanonical()
  // * TODO(crbug.com/1244172): Add exceptions once IsCanonical() starts
  // enforcing them.
  bool IsCanonicalForFromStorage() const;

  // Returns whether the effective SameSite mode is SameSite=None (i.e. no
  // SameSite restrictions).
  bool IsEffectivelySameSiteNone(CookieAccessSemantics access_semantics =
                                     CookieAccessSemantics::UNKNOWN) const;

  CookieEffectiveSameSite GetEffectiveSameSiteForTesting(
      CookieAccessSemantics access_semantics =
          CookieAccessSemantics::UNKNOWN) const;

  // Returns the cookie line (e.g. "cookie1=value1; cookie2=value2") represented
  // by |cookies|. The string is built in the same order as the given list.
  static std::string BuildCookieLine(const CookieList& cookies);

  // Same as above but takes a CookieAccessResultList
  // (ignores the access result).
  static std::string BuildCookieLine(const CookieAccessResultList& cookies);

  // Takes a single CanonicalCookie and returns a cookie line containing the
  // attributes of |cookie| formatted like a http set cookie header.
  // (e.g. "cookie1=value1; domain=abc.com; path=/; secure").
  static std::string BuildCookieAttributesLine(const CanonicalCookie& cookie);

 private:
  FRIEND_TEST_ALL_PREFIXES(CanonicalCookieTest,
                           TestGetAndAdjustPortForTrustworthyUrls);
  FRIEND_TEST_ALL_PREFIXES(CanonicalCookieTest, TestPrefixHistograms);
  FRIEND_TEST_ALL_PREFIXES(CanonicalCookieTest, TestHasHiddenPrefixName);

  // The special cookie prefixes as defined in
  // https://tools.ietf.org/html/draft-west-cookie-prefixes
  //
  // This enum is being histogrammed; do not reorder or remove values.
  enum CookiePrefix {
    COOKIE_PREFIX_NONE = 0,
    COOKIE_PREFIX_SECURE,
    COOKIE_PREFIX_HOST,
    COOKIE_PREFIX_LAST,
    COOKIE_PREFIX_MONITORED, //BrowserOnly - add new prefixes
    COOKIE_PREFIX_BROWSER
  };

  // Returns the CookiePrefix (or COOKIE_PREFIX_NONE if none) that
  // applies to the given cookie |name|.
  static CookiePrefix GetCookiePrefix(const std::string& name) {
    return GetCookiePrefix(name,
                           base::FeatureList::IsEnabled(
                               net::features::kCaseInsensitiveCookiePrefix));
  }

  // Returns the CookiePrefix (or COOKIE_PREFIX_NONE if none) that
  // applies to the given cookie |name|. If `check_insensitively` is true then
  // the string comparison will be performed case insensitively.
  static CookiePrefix GetCookiePrefix(const std::string& name,
                                      bool check_insensitively);
  // Records histograms to measure how often cookie prefixes appear in
  // the wild and how often they would be blocked.
  static void RecordCookiePrefixMetrics(CookiePrefix prefix_case_sensitive,
                                        CookiePrefix prefix_case_insensitive,
                                        bool is_insensitive_prefix_valid);
  // Returns true if a prefixed cookie does not violate any of the rules
  // for that cookie.
  static bool IsCookiePrefixValid(CookiePrefix prefix,
                                  const GURL& url,
                                  const ParsedCookie& parsed_cookie);
  static bool IsCookiePrefixValid(CookiePrefix prefix,
                                  const GURL& url,
                                  bool secure,
				  bool httponly,
				  bool browser, // BrowserOnly - update method signature
				  CookieMonitored monitor,
				  const std::string& monitoredMessage,
                                  const std::string& domain,
                                  const std::string& path);

  // Returns the effective SameSite mode to apply to this cookie. Depends on the
  // value of the given SameSite attribute and the access semantics of the
  // cookie.
  // Note: If you are converting to a different representation of a cookie, you
  // probably want to use SameSite() instead of this method. Otherwise, if you
  // are considering using this method, consider whether you should use
  // IncludeForRequestURL() or IsSetPermittedInContext() instead of doing the
  // SameSite computation yourself.
  CookieEffectiveSameSite GetEffectiveSameSite(
      CookieAccessSemantics access_semantics) const;

  // Returns the appropriate port value for the given `source_url` depending on
  // if the url is considered trustworthy or not.
  //
  // This function normally returns source_url.EffectiveIntPort(), but it can
  // return a different port value if:
  // * `source_url`'s scheme isn't cryptographically secure
  // * `url_is_trustworthy` is true
  // * `source_url`'s port is the default port for the scheme i.e.: 80
  // If all these conditions are true then the returned value will be 443 to
  // indicate that we're treating `source_url` as if it was secure.
  static int GetAndAdjustPortForTrustworthyUrls(const GURL& source_url,
                                                bool url_is_trustworthy);

  // Checks for values that could be misinterpreted as a cookie name prefix.
  static bool HasHiddenPrefixName(const base::StringPiece cookie_value);

  // Returns whether the cookie was created at most |age_threshold| ago.
  bool IsRecentlyCreated(base::TimeDelta age_threshold) const;

  // Returns true iff the cookie is a partitioned cookie with a nonce or that
  // does not violate the semantics of the Partitioned attribute:
  // - Must have the Secure attribute OR the cookie partition contains a nonce.
  static bool IsCookiePartitionedValid(const GURL& url,
                                       const ParsedCookie& parsed_cookie,
                                       bool partition_has_nonce);
  static bool IsCookiePartitionedValid(const GURL& url,
                                       bool secure,
                                       bool is_partitioned,
                                       bool partition_has_nonce);

  // Keep defaults here in sync with
  // services/network/public/interfaces/cookie_manager.mojom.
  std::string name_;
  std::string value_;
  std::string domain_;
  std::string path_;
  base::Time creation_date_;
  base::Time expiry_date_;
  base::Time last_access_date_;
  base::Time last_update_date_;
  bool secure_{false};
  bool httponly_{false};
  bool browseronly_{false}; // BrowserOnly - add variable and default to false
  CookieSameSite same_site_{CookieSameSite::NO_RESTRICTION};
  CookiePriority priority_{COOKIE_PRIORITY_MEDIUM};
  // This will be absl::nullopt for all cookies not set with the Partitioned
  // attribute or without a nonce. If the value is non-null, then the cookie
  // will only be delivered when the top-frame site matches the partition key
  // and the nonce (if present). If the partition key is non-null and opaque,
  // this means the Partitioned cookie was created on an opaque origin or with
  // a nonce.
  absl::optional<CookiePartitionKey> partition_key_;
  CookieSourceScheme source_scheme_{CookieSourceScheme::kUnset};
  // This can be [0,65535], PORT_UNSPECIFIED, or PORT_INVALID.
  // PORT_UNSPECIFIED is used for cookies which already existed in the cookie
  // store prior to this change and therefore their port is unknown.
  // PORT_INVALID is an error for when an out of range port is provided.
  int source_port_{url::PORT_UNSPECIFIED};
  MonitoredData monitored_data_; // BrowserOnly - add variable decleration
};

// Used to pass excluded cookie information when it's possible that the
// canonical cookie object may not be available.
struct NET_EXPORT CookieAndLineWithAccessResult {
  CookieAndLineWithAccessResult();
  CookieAndLineWithAccessResult(absl::optional<CanonicalCookie> cookie,
                                std::string cookie_string,
                                CookieAccessResult access_result);
  CookieAndLineWithAccessResult(
      const CookieAndLineWithAccessResult& cookie_and_line_with_access_result);

  CookieAndLineWithAccessResult& operator=(
      const CookieAndLineWithAccessResult& cookie_and_line_with_access_result);

  CookieAndLineWithAccessResult(
      CookieAndLineWithAccessResult&& cookie_and_line_with_access_result);

  ~CookieAndLineWithAccessResult();

  absl::optional<CanonicalCookie> cookie;
  std::string cookie_string;
  CookieAccessResult access_result;
};

struct CookieWithAccessResult {
  CanonicalCookie cookie;
  CookieAccessResult access_result;
};

// Provided to allow gtest to create more helpful error messages, instead of
// printing hex.
inline void PrintTo(const CanonicalCookie& cc, std::ostream* os) {
  *os << "{ name=" << cc.Name() << ", value=" << cc.Value() << " }";
}
inline void PrintTo(const CookieWithAccessResult& cwar, std::ostream* os) {
  *os << "{ ";
  PrintTo(cwar.cookie, os);
  *os << ", ";
  PrintTo(cwar.access_result, os);
  *os << " }";
}
inline void PrintTo(const CookieAndLineWithAccessResult& calwar,
                    std::ostream* os) {
  *os << "{ ";
  if (calwar.cookie) {
    PrintTo(*calwar.cookie, os);
  } else {
    *os << "nullopt";
  }
  *os << ", " << calwar.cookie_string << ", ";
  PrintTo(calwar.access_result, os);
  *os << " }";
}

}  // namespace net

#endif  // NET_COOKIES_CANONICAL_COOKIE_H_
