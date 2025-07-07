import type { Telecom } from "@/utils/types.ts";
import type React from "react";

const ContactInformation: React.FC<{ telecom: Telecom }> = ({ telecom }) => {
  return (
    <>
      {telecom?.email && <div>Email: {telecom.email}</div>}
      {telecom?.phone_public && <div>Public Phone: {telecom.phone_public}</div>}
      {telecom?.phone_private && (
        <div>Private Phone: {telecom.phone_private}</div>
      )}
      {telecom?.website && <div>Website: {telecom.website}</div>}
      {(!telecom ||
        (!telecom.email &&
          !telecom.phone_public &&
          !telecom.phone_private &&
          !telecom.website)) &&
        "None Provided"}
    </>
  );
};
export default ContactInformation;
